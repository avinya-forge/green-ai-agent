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

        import types

        # Iterate over generator to find files, avoiding full list loading early on,
        # but we do need the length for total_files and progress tracking.
        # Actually, let's just use the generator to get supported files.
        if isinstance(path, str):
            files_gen = self.file_discoverer.get_files(path)
            scan_metadata_path = path
        else:
            def chained_gen():
                for p in path:
                    yield from self.file_discoverer.get_files(p)
            files_gen = chained_gen()
            scan_metadata_path = f"Multiple paths ({len(path)})"

        files_to_scan = [f for f in files_gen if self._is_supported_file(f)]
        total_files = len(files_to_scan)

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
        # Use os.cpu_count() explicitly if config not set
        config_concurrency = self.config.get('concurrency')
        if config_concurrency:
            num_workers = int(config_concurrency)
        else:
            # Default to CPU count, capped at 32 for safety
            # Reserve 1 core for the main process if possible
            cpus = os.cpu_count() or 1
            num_workers = max(1, min(32, cpus - 1)) if cpus > 1 else 1

        if progress_callback:
            progress_callback("Scanning files...", 10)

        processed_count = 0

        # Get rules for the language
        language_rules = self.rule_repo.get_rules(self.language)

        # Calculate chunksize for executor.map
        # A simple heuristic: ensure each worker gets a reasonable batch
        # to minimize IPC overhead.
        # If total files is small, chunksize=1 is fine.
        # If large, try to give each worker at least 4 items per chunk,
        # but balance load.
        config_chunk_size = self.config.get('chunk_size')
        if config_chunk_size:
            chunksize = int(config_chunk_size)
        else:
            chunksize = max(1, total_files // (num_workers * 4))

        # Use 'spawn' context
        mp_context = multiprocessing.get_context('spawn')

        # Helper for map
        # We need a wrapper function that unpacks arguments for map
        # since scan_file_worker takes multiple args
        # But wait, we can't pickle a local lambda easily.
        # So we define a partial or use starmap if available (ProcessPoolExecutor doesn't support starmap directly until 3.11+ maybe?)
        # Actually executor.map takes *iterables.
        # So we can pass iterables for each argument.

        total_scan_files = len(files_to_scan)

        if total_scan_files > 0:
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=num_workers, mp_context=mp_context
            ) as executor:
                # Use executor.map with chunksize
                # We need to pass constant arguments as repeated iterables
                # OR better: make scan_file_worker take a single tuple/dict and unpack it?
                # Changing worker signature might break tests or other calls if any.
                # Let's check worker.py. It's a top level function.
                # We can wrap it here locally? No, pickling issues.
                # We can use a list comprehension with submit as before but that doesn't support chunksize directly in submit.
                # executor.map supports chunksize.

                # To use executor.map with multiple arguments, we pass multiple iterables.
                # itertools.repeat can be used for constant arguments.
                import itertools

                results_iterator = executor.map(
                    scan_file_worker,
                    files_to_scan,
                    itertools.repeat(self.language),
                    itertools.repeat(self.config),
                    itertools.repeat(language_rules),
                    chunksize=chunksize
                )

                for file_path, file_result in zip(files_to_scan, results_iterator):
                    try:
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
        elif self.language == 'java':
            return ['java', path]
        elif self.language == 'go':
            return ['go', 'run', path]
        elif self.language == 'csharp':
            return ['dotnet', 'script', path]
        else:
            return None

    def _is_supported_file(self, file_path):
        if self.language == 'python':
            return file_path.endswith('.py')
        elif self.language == 'javascript':
            return file_path.endswith('.js')
        elif self.language == 'typescript':
            return file_path.endswith('.ts') or file_path.endswith('.tsx')
        elif self.language == 'java':
            return file_path.endswith('.java')
        elif self.language == 'go':
            return file_path.endswith('.go')
        elif self.language == 'csharp':
            return file_path.endswith('.cs')
        return False
