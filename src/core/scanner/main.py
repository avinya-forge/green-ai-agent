import os
import sys
import concurrent.futures
import multiprocessing
from multiprocessing import cpu_count
from typing import Optional, List, Union

from src.core.rules import RuleRepository
from src.core.remediation.engine import RemediationEngine
from src.core.analyzer import EmissionAnalyzer
from src.core.config import ConfigLoader
from src.core.tracking import create_tracker
from src.core.calibration import CalibrationAgent
from src.utils.logger import logger

from src.core.scanner.worker import scan_file_worker
from src.core.scanner.discovery import FileDiscoverer


class Scanner:
    def __init__(
        self, language: Optional[str] = None, runtime: bool = False,
        config_path: Optional[str] = None, profile: bool = False
    ):
        """
        Initialize scanner.

        Args:
            language: Language to scan (python, javascript).
            runtime: Enable runtime monitoring.
            config_path: Path to .green-ai.yaml config file.
            profile: Enable emissions profiling.
        """
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load()

        # Use provided language or load from config
        self.language = language or \
            self.config_loader.get_enabled_languages()[0]
        self.runtime = runtime
        self.profile = profile
        self.rule_repo = RuleRepository()
        self.remediation_engine = RemediationEngine()

        # Load system calibration
        self.calibration_agent = CalibrationAgent()
        self.emission_analyzer = EmissionAnalyzer(
            calibration_coefficient=self.calibration_agent.get_coefficient()
        )

        self.file_discoverer = FileDiscoverer(self.config_loader)

    def scan(self, path: Union[str, List[str]], progress_callback=None):
        """
        Scan a directory, file, or list of paths.

        Args:
            path: Path or list of paths to scan.
            progress_callback: Optional function(message, percentage).

        Returns:
            Dictionary with scan results.
        """
        # Create appropriate tracker
        tracker = create_tracker(enable_profiling=self.profile)
        tracker.start()

        logger.info(f"Starting scan on {path}...")

        files = []
        scan_metadata_path = ""

        if isinstance(path, str):
            files = self.file_discoverer.get_files(path)
            scan_metadata_path = path
        else:
            files = []
            for p in path:
                files.extend(self.file_discoverer.get_files(p))
            scan_metadata_path = f"Multiple paths ({len(path)})"

        total_files = len(files)

        if total_files == 0:
            tracker.stop()
            return {
                'issues': [],
                'scanning_emissions': 0,
                'codebase_emissions': 0,
                'per_file_emissions': {},
                'metadata': {'total_files': 0}
            }

        issues = []
        per_file_emissions = {}
        total_codebase_emissions = 0.0

        # Determine number of workers
        num_workers = min(32, (cpu_count() or 1) + 4)

        if progress_callback:
            progress_callback("Scanning files...", 10)

        processed_count = 0

        # Get rules for the language
        language_rules = self.rule_repo.get_rules(self.language)

        # Use 'spawn' context
        mp_context = multiprocessing.get_context('spawn')
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=num_workers, mp_context=mp_context
        ) as executor:
            future_to_file = {
                executor.submit(
                    scan_file_worker,
                    f,
                    self.language,
                    self.config,
                    language_rules
                ): f for f in files if self._is_supported_file(f)
            }

            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_result = future.result()
                    issues.extend(file_result['issues'])
                    per_file_emissions[file_path] = file_result['emissions']
                    total_codebase_emissions += file_result['emissions']

                    processed_count += 1
                    if progress_callback and total_files > 0:
                        percentage = 10 + int(
                            (processed_count / total_files) * 80
                        )
                        progress_callback(
                            f"Processing {os.path.basename(file_path)}",
                            percentage
                        )
                except Exception as exc:
                    logger.error(f"{file_path} generated an exception: {exc}")

        if progress_callback:
            progress_callback("Finalizing scan results...", 95)

        # Distribute codebase emissions across issues
        issues = self.emission_analyzer.get_per_line_emissions(
            issues, total_codebase_emissions
        )

        # Runtime monitoring if enabled
        runtime_metrics = {}
        if self.runtime and self.language == 'python':
            runtime_metrics = self._run_with_monitoring(path)

        tracking_result = tracker.stop()
        # Extract emissions value for backward compatibility
        scanning_emissions = tracking_result.get('emissions', 0.0) \
            if isinstance(tracking_result, dict) else tracking_result

        results = {
            'issues': issues,
            'scanning_emissions': scanning_emissions,
            'scanning_emissions_detailed': tracking_result,
            'codebase_emissions': total_codebase_emissions,
            'per_file_emissions': per_file_emissions,
            'runtime_metrics': runtime_metrics,
            'metadata': {
                'total_files': total_files,
                'language': self.language,
                'path': scan_metadata_path
            }
        }

        if progress_callback:
            progress_callback("Scan complete", 100)

        return results

    def _run_with_monitoring(self, path):
        """Safely execute code and monitor basic runtime metrics."""
        if isinstance(path, list):
            return {
                'error': 'Runtime monitoring requires a single entry point '
                         'path, not a list.'
            }

        if not os.path.isfile(path):
            return {'error': 'Runtime monitoring requires a single file path'}

        command = self._get_run_command(path)
        if not command:
            return {
                'error': f'Runtime monitoring not supported for language '
                         f'{self.language}'
            }

        try:
            import subprocess
            import time

            # Use profiling tracker for runtime monitoring
            runtime_tracker = create_tracker(enable_profiling=True)
            runtime_tracker.start()

            start_time = time.time()

            # Execute the script with timeout
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=30
            )

            execution_time = time.time() - start_time
            runtime_emissions = runtime_tracker.stop()

            return {
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'return_code': result.returncode,
                'execution_time': f"{execution_time:.2f}s",
                'emissions': runtime_emissions
            }

        except subprocess.TimeoutExpired:
            runtime_tracker.stop()  # Stop tracker even on timeout
            return {
                'error': 'Execution timed out after 30 seconds',
                'execution_time': '>30s',
                'emissions': 0.0
            }
        except Exception as e:
            try:
                runtime_tracker.stop()
            except Exception:
                pass
            return {
                'error': str(e),
                'execution_time': 'N/A',
                'emissions': 0.0
            }

    def _get_run_command(self, path):
        if self.language == 'python':
            return [sys.executable, path]
        elif self.language == 'javascript':
            return ['node', path]
        elif self.language == 'typescript':
            return ['npx', 'ts-node', path]
        else:
            return None

    def _is_supported_file(self, file_path):
        if self.language == 'python':
            return file_path.endswith('.py')
        elif self.language == 'javascript':
            return file_path.endswith('.js')
        elif self.language == 'typescript':
            return file_path.endswith('.ts') or file_path.endswith('.tsx')
        return False
