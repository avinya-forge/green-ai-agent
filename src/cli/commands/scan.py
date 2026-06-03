import click
import sys
import os
from typing import Dict, Any
from src.core.scanner import Scanner
from src.core.config import ConfigLoader
from src.core.git_operations import GitOperations, GitException
from src.core.project_manager import ProjectManager
from src.ui.state import set_last_scan_results
from src.utils.security import sanitize_project_name, \
    is_safe_git_url


def _run_standards_sync(cfg: Dict[str, Any], fail_on_stale: bool, max_age_days: int) -> None:
    """Auto-sync standards if configured; enforce fail_on_stale if requested."""
    try:
        from src.standards.sync_engine import StandardsSyncEngine
        # Use 'standards_sync' key to avoid clash with existing 'standards' List[str]
        standards_cfg = cfg.get('standards_sync', {})
        if not isinstance(standards_cfg, dict):
            standards_cfg = {}
        auto_sync = standards_cfg.get('auto_sync', False)
        interval = int(standards_cfg.get('sync_interval_hours', 24))

        engine = StandardsSyncEngine(sync_interval_hours=interval)

        if auto_sync:
            click.echo("[standards] Auto-syncing standards...", err=True)
            results = engine.sync_all(force=False)
            ok = sum(1 for e in results.values() if e.sync_ok)
            total = len(results)
            click.echo(f"[standards] {ok}/{total} sources synced.", err=True)

        if fail_on_stale:
            stale = engine.check_stale(max_age_days=max_age_days)
            stale_names = [n for n, s in stale.items() if s]
            if stale_names:
                click.echo(
                    f"[standards] STALE sources (>{max_age_days}d): "
                    f"{', '.join(stale_names)}",
                    err=True
                )
                click.echo(
                    "[standards] Run: green-ai standards sync",
                    err=True
                )
                sys.exit(2)
    except ImportError:
        pass  # Standards engine optional dependency


@click.command()
@click.argument(
    'paths', nargs=-1, type=click.Path(exists=False), required=False
)
@click.option(
    '--git-url', default=None,
    help='Git repository URL (supports @branch syntax)'
)
@click.option(
    '--branch', default=None,
    help='Specific branch to scan (overrides @branch in URL)'
)
@click.option(
    '--project-name', default=None,
    help='Name to register project in registry'
)
@click.option(
    '--language', default=None,
    help='Programming language (python, javascript). Default: from config.'
)
@click.option(
    '--config', type=click.Path(exists=True), default=None,
    help='Path to .green-ai.yaml config file'
)
@click.option(
    '--disable-rule', multiple=True,
    help='Disable specific rule(s) (overrides config)'
)
@click.option(
    '--enable-rule', multiple=True,
    help='Enable specific rule(s) (overrides config)'
)
@click.option(
    '--runtime', is_flag=True, help='Include runtime monitoring'
)
@click.option(
    '--profile', is_flag=True,
    help='Enable emissions profiling (adds 10-15% overhead, default fast mode)'
)
@click.option(
    '--perf-profile', is_flag=True,
    help='Enable internal cProfile for performance analysis'
)
@click.option(
    '--fix-all', is_flag=True, help='Fix all issues automatically'
)
@click.option(
    '--fix-specific', multiple=True, help='Fix specific issue IDs'
)
@click.option(
    '--manual', is_flag=True, help='Manual mode: show issues without fixing'
)
@click.option(
    '--export',
    default=None,
    help='Export results: csv, csv:path.csv, html, html:path.html'
)
@click.option('--format', default=None, help='[Deprecated] Output format')
@click.option('--output', default=None, help='[Deprecated] Output file path')
@click.option(
    '--telemetry/--no-telemetry', default=True,
    help='Enable/Disable telemetry collection'
)
@click.option(
    '--fail-on',
    type=click.Choice(['critical', 'high', 'medium', 'low'], case_sensitive=False),
    help='Exit with error code 1 if issues of this severity or higher are found.'
)
@click.option(
    '--checks',
    default='all',
    show_default=True,
    help=(
        'Comma-separated check categories to run: '
        'energy, security, quality, ai, all. '
        'Example: --checks energy,ai'
    )
)
@click.option(
    '--fail-on-stale-standards',
    is_flag=True, default=False,
    help=(
        'Exit with code 2 if any standards source is older than 7 days. '
        'Use with --standards-max-age to customise the threshold.'
    )
)
@click.option(
    '--standards-max-age', default=7, type=int, show_default=True,
    help='Max age in days for standards before they are considered stale.'
)
def scan(
    paths, git_url, branch, project_name, language, config, disable_rule,
    enable_rule, runtime, profile, perf_profile, fix_all, fix_specific,
    manual, export, format, output, telemetry, fail_on, checks,
    fail_on_stale_standards, standards_max_age
):
    """Scan a codebase for green software violations."""
    scan_path = None
    cleanup_after = False

    try:
        # Handle backward compatibility for --format and --output
        if format and not export:
            if output:
                export = f"{format}:{output}"
            else:
                export = format

        # Validate inputs
        if not paths and not git_url:
            click.echo("Error: Either PATH(s) or --git-url must be provided", err=True)
            sys.exit(1)

        # Sanitize inputs
        if git_url and not is_safe_git_url(git_url):
            click.echo(f"Error: Invalid or unsafe git URL: {git_url}", err=True)
            sys.exit(1)

        if project_name:
            project_name = sanitize_project_name(project_name)

        # Determine scan location
        if git_url:
            # Clone and prepare Git repository
            click.echo(f"Preparing Git repository: {git_url}")
            try:
                # Apply branch override if provided
                if branch:
                    git_url = f"{git_url.split('@')[0]}@{branch}"

                scan_path, repo_url, detected_branch = \
                    GitOperations.clone_and_checkout(git_url)
                click.echo(f"[OK] Repository cloned to: {scan_path}")
                click.echo(f"[OK] Branch: {detected_branch}")

                cleanup_after = True  # Mark for cleanup after scan
            except GitException as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)
        else:
            # Handle single or multiple paths
            if len(paths) == 1:
                scan_path = paths[0]
            else:
                scan_path = list(paths)

            repo_url = None
            detected_branch = None
            cleanup_after = False

        # Load configuration
        config_loader = ConfigLoader(config)
        cfg = config_loader.load()

        # Parse --checks into a list and inject into config
        checks_list = [c.strip().lower() for c in checks.split(',') if c.strip()]
        cfg['checks'] = checks_list

        # Standards auto-sync (STD-005)
        _run_standards_sync(cfg, fail_on_stale_standards, standards_max_age)

        # Override telemetry setting if flag is explicitly set
        if telemetry is False:
            os.environ['GREEN_AI_TELEMETRY'] = 'false'

        # Determine language
        if language is None:
            language = cfg.get('languages', ['python'])[0]

        click.echo(f"Scanning {scan_path} for {language} code...", err=True)
        if profile:
            click.echo("Emissions profiling enabled", err=True)

        # Create scanner
        scanner = Scanner(
            language=language, runtime=runtime, config_path=config,
            profile=profile
        )
        scanner.config['checks'] = checks_list

        # Apply CLI rule overrides
        if disable_rule or enable_rule:
            for rule_id in disable_rule:
                if rule_id not in scanner.config_loader.config.get('rules', {}).get('disabled', []):
                    if 'rules' not in scanner.config_loader.config:
                        scanner.config_loader.config['rules'] = {}
                    if 'disabled' not in scanner.config_loader.config['rules']:
                        scanner.config_loader.config['rules']['disabled'] = []
                    scanner.config_loader.config['rules']['disabled'].append(rule_id)
            for rule_id in enable_rule:
                if rule_id not in scanner.config_loader.config.get('rules', {}).get('enabled', []):
                    if 'rules' not in scanner.config_loader.config:
                        scanner.config_loader.config['rules'] = {}
                    if 'enabled' not in scanner.config_loader.config['rules']:
                        scanner.config_loader.config['rules']['enabled'] = []
                    scanner.config_loader.config['rules']['enabled'].append(rule_id)

        if perf_profile:
            import cProfile
            import pstats
            from pathlib import Path
            click.echo("Running with cProfile enabled...", err=True)
            profiler = cProfile.Profile()
            profiler.enable()

        results = scanner.scan(scan_path)

        if perf_profile:
            profiler.disable()
            stats = pstats.Stats(profiler).sort_stats('cumtime')
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            stats_file = output_dir / 'scanner_profile.stats'
            stats.dump_stats(stats_file)
            click.echo(f"\n[PERF] Profile stats saved to {stats_file}", err=True)

        # Update project registry
        if project_name:
            manager = ProjectManager()
            project = manager.get_project(project_name)
            if project is None:
                project_url = repo_url or (f"Multiple paths ({len(scan_path)})" if isinstance(scan_path, list) else scan_path)
                project = manager.add_project(name=project_name, repo_url=project_url, branch=detected_branch, language=language)
                click.echo(f"[OK] Project registered: {project_name}", err=True)

            manager.update_project_scan(project_name, violations=results['issues'], emissions=results.get('codebase_emissions', 0))
            click.echo(f"[OK] Project scan recorded: {len(results['issues'])} violations", err=True)

        set_last_scan_results(results)
        click.echo(f"Scan complete. Found {len(results['issues'])} issues.", err=True)

        # Emissions report
        scanning_e = results.get('scanning_emissions', 0)
        codebase_e = results.get('codebase_emissions', 0)
        click.echo("\n=== Carbon Emissions Report ===", err=True)
        click.echo(f"Scanning Process Emissions: {scanning_e:.9f} kg CO2", err=True)
        click.echo(f"Estimated Codebase Emissions: {codebase_e:.9f} kg CO2", err=True)
        click.echo(f"Total: {scanning_e + codebase_e:.9f} kg CO2", err=True)

        # Check for failure threshold
        if fail_on:
            severity_map = {'critical': 4, 'major': 3, 'high': 3, 'medium': 2, 'minor': 1, 'low': 1, 'info': 0}
            threshold_val = severity_map.get(fail_on.lower(), 0)
            failed = any(severity_map.get(i.get('severity', 'low').lower(), 1) >= threshold_val for i in results['issues'])

            if failed:
                click.echo(f"\n[FAILURE] Scan failed due to violations of severity '{fail_on}' or higher.", err=True)
                sys.exit(1)

    except Exception as e:
        click.echo(f"Error during scan: {e}", err=True)
        sys.exit(1)
    finally:
        if cleanup_after and scan_path and git_url:
            click.echo("\nCleaning up temporary repository...", err=True)
            GitOperations.cleanup_repo(scan_path)
            click.echo("[OK] Cleanup complete", err=True)
