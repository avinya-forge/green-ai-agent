import os
import sys
import concurrent.futures
import multiprocessing
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
from src.core.scanner.baseline_helper import load_baseline, filter_with_baseline


class Scanner:
    def __init__(
        self,
        language: str = 'python',
        runtime: bool = False,
        config_path: Optional[str] = None,
        profile: bool = False
    ):
        self.language = language
        self.runtime = runtime
        self.profile = profile
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load()
        self.rule_repo = RuleRepository()
        self.emission_analyzer = EmissionAnalyzer()
        self.file_discoverer = FileDiscoverer(
            config_loader=self.config_loader
        )
        self.remediation_engine = RemediationEngine()

    def scan(self, path: Union[str, List[str]], progress_callback=None) -> dict:
        """
        Run a full scan on the given path.

        Args:
            path: Path to scan (file or directory) or list of paths
            progress_callback: Optional function(message, percentage) for progress

        Returns:
            Dictionary of scan results
        """
        tracker = create_tracker(enable_profiling=self.profile)
        tracker.start()

        logger.info(f"Starting scan on {path}...")

        scan_metadata_path = ""

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

        config_concurrency = self.config.get('concurrency')
        if config_concurrency:
            num_workers = int(config_concurrency)
        else:
            cpus = os.cpu_count() or 1
            num_workers = max(1, min(32, cpus - 1)) if cpus > 1 else 1

        if progress_callback:
            progress_callback("Scanning files...", 10)

        processed_count = 0
        language_rules = self.rule_repo.get_rules(self.language)

        config_chunk_size = self.config.get('chunk_size')
        if config_chunk_size:
            chunksize = int(config_chunk_size)
        else:
            cpus = os.cpu_count() or 1
            chunksize = max(1, total_files // (cpus * 4))

        mp_context = multiprocessing.get_context('spawn')
        total_scan_files = len(files_to_scan)

        if total_scan_files > 0:
            kwargs = {}
            if sys.version_info >= (3, 11):
                kwargs['max_tasks_per_child'] = 50

            with concurrent.futures.ProcessPoolExecutor(
                max_workers=num_workers, mp_context=mp_context, **kwargs
            ) as executor:
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

        # Apply baseline filtering (BASE-002)
        baseline = load_baseline()
        issues, skipped_count, fixed_count = filter_with_baseline(issues, baseline)

        # Distribute codebase emissions across issues
        issues = self.emission_analyzer.get_per_line_emissions(
            issues, total_codebase_emissions
        )

        runtime_metrics = {}
        if self.runtime and self.language == 'python':
            runtime_metrics = self._run_with_monitoring(path)

        tracking_result = tracker.stop()
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
                'path': scan_metadata_path,
                'baseline_skipped': skipped_count,
                'baseline_fixed': fixed_count
            }
        }

        if skipped_count > 0 or fixed_count > 0:
            logger.info(f"Baseline Delta: {len(issues)} new, {skipped_count} ignored, {fixed_count} fixed.")

        if progress_callback:
            progress_callback("Scan complete", 100)

        return results

    def _run_with_monitoring(self, path):
        if isinstance(path, list):
            return {
                'error': 'Runtime monitoring requires a single entry point path'
            }

        if not os.path.isfile(path):
            return {'error': 'Runtime monitoring requires a single file path'}

        command = self._get_run_command(path)
        if not command:
            return {
                'error': f'Runtime monitoring not supported for language {self.language}'
            }

        try:
            import subprocess
            import time

            runtime_tracker = create_tracker(enable_profiling=True)
            runtime_tracker.start()

            start_time = time.time()
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
            runtime_tracker.stop()
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
