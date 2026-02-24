import click
import sys
from src.core.scanner import Scanner
from src.core.config import ConfigLoader
from src.core.git_operations import GitOperations, GitException
from src.core.project_manager import ProjectManager
from src.core.export import CSVExporter, HTMLReporter, JSONExporter, \
    JUnitXMLExporter, PDFExporter
from src.ui.state import set_last_scan_results
from src.utils.security import sanitize_path, sanitize_project_name, \
    is_safe_git_url


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
def scan(
    paths, git_url, branch, project_name, language, config, disable_rule,
    enable_rule, runtime, profile, perf_profile, fix_all, fix_specific,
    manual, export, format, output, telemetry
):
    """Scan a codebase for green software violations.

    PATHS can be one or more local directories/files, or omitted if using
    --git-url.
    """
    try:
        # Handle backward compatibility for --format and --output
        if format and not export:
            if output:
                export = f"{format}:{output}"
            else:
                export = format

        # Validate inputs
        if not paths and not git_url:
            click.echo(
                "Error: Either PATH(s) or --git-url must be provided",
                err=True
            )
            sys.exit(1)

        # Sanitize inputs
        if git_url and not is_safe_git_url(git_url):
            click.echo(
                f"Error: Invalid or unsafe git URL: {git_url}",
                err=True
            )
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

        # Override telemetry setting if flag is explicitly set
        import os
        if telemetry is False:
             os.environ['GREEN_AI_TELEMETRY'] = 'false'
        # Note: If telemetry is True (default), we don't force it to allow config/env var to disable it.

        # Determine language
        if language is None:
            language = cfg.get('languages', ['python'])[0]

        # Only print logs if not exporting to stdout
        verbose = True

        if verbose:
            click.echo(
                f"Scanning {scan_path} for {language} code...", err=True
            )
        if profile:
            click.echo("Emissions profiling enabled", err=True)

        # Create scanner with config and profiling flag
        scanner = Scanner(
            language=language, runtime=runtime, config_path=config,
            profile=profile
        )

        # Apply CLI rule overrides if provided
        if disable_rule or enable_rule:
            for rule_id in disable_rule:
                if rule_id not in scanner.config_loader.get(
                    'rules.disabled', []
                ):
                    scanner.config_loader.config['rules']['disabled'].append(
                        rule_id
                    )
            for rule_id in enable_rule:
                if rule_id not in scanner.config_loader.get(
                    'rules.enabled', []
                ):
                    scanner.config_loader.config['rules']['enabled'].append(
                        rule_id
                    )

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

            # Ensure output directory exists
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            stats_file = output_dir / 'scanner_profile.stats'
            stats.dump_stats(stats_file)

            click.echo(f"\n[PERF] Profile stats saved to {stats_file}", err=True)
            click.echo("[PERF] Top 20 functions by cumulative time:", err=True)
            stats.print_stats(20)

        # Update project registry if project name provided
        if project_name:
            manager = ProjectManager()
            project = manager.get_project(project_name)

            if project is None:
                # Handle repo_url for multiple paths
                if repo_url:
                    project_url = repo_url
                elif isinstance(scan_path, list):
                    project_url = f"Multiple paths ({len(scan_path)})"
                else:
                    project_url = scan_path

                # Create new project
                project = manager.add_project(
                    name=project_name,
                    repo_url=project_url,
                    branch=detected_branch,
                    language=language
                )
                click.echo(
                    f"[OK] Project registered: {project_name}", err=True
                )

            # Update with scan results
            violations_count = len(results['issues'])
            emissions = results.get('codebase_emissions', 0)
            manager.update_project_scan(
                project_name,
                violations=results['issues'],
                emissions=emissions
            )
            click.echo(
                f"[OK] Project scan recorded: {violations_count} violations, "
                f"{emissions:.9f} kg CO2",
                err=True
            )

        # Store results for dashboard
        set_last_scan_results(results)

        click.echo("Scan complete.", err=True)
        click.echo(f"Found {len(results['issues'])} issues.", err=True)

        # Display dual emission metrics
        scanning_emissions = results.get('scanning_emissions', 0)
        codebase_emissions = results.get('codebase_emissions', 0)

        click.echo("\n=== Carbon Emissions Report ===", err=True)
        click.echo(
            f"Scanning Process Emissions: {scanning_emissions:.9f} kg CO2",
            err=True
        )
        click.echo(
            f"Estimated Codebase Emissions: {codebase_emissions:.9f} kg CO2",
            err=True
        )
        click.echo(
            f"Total: {scanning_emissions + codebase_emissions:.9f} kg CO2",
            err=True
        )

        if codebase_emissions > 0:
            total_e = scanning_emissions + codebase_emissions
            ratio = (codebase_emissions / total_e) * 100 if total_e > 0 else 0
            click.echo(
                f"Code Emissions Ratio: {ratio:.1f}% of total", err=True
            )

        # Per-file emissions
        if results.get('per_file_emissions'):
            click.echo("\nEmissions by File:", err=True)
            for file_path, emissions in results['per_file_emissions'].items():
                click.echo(f"  {file_path}: {emissions:.9f} kg CO2", err=True)

        # Runtime metrics output
        if 'runtime_metrics' in results and results['runtime_metrics']:
            click.echo("\n=== Runtime Metrics ===", err=True)
            click.echo(
                f"Execution Time: "
                f"{results['runtime_metrics'].get('execution_time', 'N/A')}",
                err=True
            )
            click.echo(
                f"Runtime Emissions: "
                f"{results['runtime_metrics'].get('emissions', 0):.6f} kg CO2",
                err=True
            )
            if results['runtime_metrics'].get('output'):
                click.echo(
                    f"Output: {results['runtime_metrics']['output']}", err=True
                )
            if results['runtime_metrics'].get('error'):
                click.echo(
                    f"Error: {results['runtime_metrics']['error']}", err=True
                )
            click.echo(
                f"Return Code: "
                f"{results['runtime_metrics'].get('return_code', 'N/A')}",
                err=True
            )

        # Handle export options
        if export:
            try:
                # Parse export format
                if ':' in export:
                    export_format, export_path = export.split(':', 1)
                    # Sanitize export_path
                    try:
                        # Allow absolute paths, but ensure validity
                        sanitized_path = sanitize_path(
                            export_path, allow_absolute=True
                        )
                        export_path = str(sanitized_path)
                    except ValueError as e:
                        click.echo(f"Error: Invalid export path: {e}", err=True)
                        sys.exit(1)
                else:
                    export_format = export
                    export_path = None

                # Validate format
                if export_format not in ['csv', 'html', 'json', 'xml', 'pdf']:
                    click.echo(
                        f"Error: Invalid export format '{export_format}'. "
                        "Use 'csv', 'html', 'json', 'xml', or 'pdf'.",
                        err=True
                    )
                    sys.exit(1)

                # Generate export
                if export_format == 'xml':
                    exporter = JUnitXMLExporter(export_path)
                    p_name = project_name or 'Scan'
                    output_file = exporter.export(results, p_name)
                    click.echo(
                        f"[OK] JUnit XML report exported: {output_file}",
                        err=True
                    )

                elif export_format == 'pdf':
                    exporter = PDFExporter(export_path)
                    p_name = project_name or 'Scan'
                    output_file = exporter.export(results, p_name)
                    if output_file:
                        click.echo(
                            f"[OK] PDF report exported: {output_file}",
                            err=True
                        )
                    else:
                        click.echo(
                            "Error: PDF export failed (check logs, possibly WeasyPrint missing).",
                            err=True
                        )
                        sys.exit(1)

                elif export_format == 'csv':
                    exporter = CSVExporter(export_path)
                    output_file = exporter.export(
                        results, project_name or 'Scan'
                    )
                    click.echo(
                        f"[OK] CSV report exported: {output_file}",
                        err=True
                    )

                    # Display statistics
                    stats = exporter.get_statistics(results)
                    click.echo("\n=== Export Statistics ===", err=True)
                    click.echo(
                        f"Total Violations: {stats['total_violations']}",
                        err=True
                    )
                    click.echo(
                        f"  Critical: {stats['severity_counts']['critical']}",
                        err=True
                    )
                    click.echo(
                        f"  High: {stats['severity_counts']['high']}",
                        err=True
                    )
                    click.echo(
                        f"  Medium: {stats['severity_counts']['medium']}",
                        err=True
                    )
                    click.echo(
                        f"  Low: {stats['severity_counts']['low']}",
                        err=True
                    )
                    click.echo(
                        f"Affected Files: {stats['affected_files']}",
                        err=True
                    )
                    click.echo(
                        f"CO2 Impact: {stats['codebase_emissions']:.9f} kg",
                        err=True
                    )

                elif export_format == 'html':
                    reporter = HTMLReporter(export_path)
                    output_file = reporter.export(
                        results, project_name or 'Scan'
                    )
                    click.echo(
                        f"[OK] HTML report exported: {output_file}",
                        err=True
                    )
                    click.echo(
                        "Open the report in your browser to view detailed "
                        "analysis and charts.",
                        err=True
                    )

                elif export_format == 'json':
                    exporter = JSONExporter(export_path)
                    output_file = exporter.export(
                        results, project_name or 'Scan'
                    )
                    click.echo(
                        f"[OK] JSON report exported: {output_file}",
                        err=True
                    )

                    if not output and not export_path:
                        import json
                        print(json.dumps(results, indent=2))

            except Exception as e:
                click.echo(f"Error during export: {str(e)}", err=True)
                sys.exit(1)

        # Detailed issue output with better formatting
        if not export or export_format != 'json':
            click.echo(f"\n{'='*80}", err=True)
            click.echo(
                f"DETAILED VIOLATIONS ({len(results['issues'])} found)",
                err=True
            )
            click.echo(f"{'='*80}", err=True)

            # Sort by severity
            severity_order = {
                'critical': 0, 'high': 1, 'medium': 2, 'low': 3
            }
            sorted_issues = sorted(
                results['issues'],
                key=lambda x: severity_order.get(x.get('severity', 'low'), 99)
            )

            for i, issue in enumerate(sorted_issues, 1):
                severity = issue.get('severity', 'unknown')

                if severity == 'critical':
                    severity_display = '[!!!] CRITICAL'
                elif severity == 'high':
                    severity_display = '[!! ] HIGH'
                elif severity == 'medium':
                    severity_display = '[!  ] MEDIUM'
                else:
                    severity_display = '[   ] LOW'

                click.echo(
                    f"\n[{i}] {issue.get('name', issue.get('id', 'unknown'))}",
                    err=True
                )
                click.echo(f"    Status: {severity_display}", err=True)
                click.echo(
                    f"    Location: {issue.get('file', 'N/A')}:"
                    f"{issue.get('line', '0')}",
                    err=True
                )
                click.echo(
                    f"    Message: {issue.get('message', 'N/A')}", err=True
                )
                click.echo(
                    f"    Energy Factor: "
                    f"{issue.get('energy_factor', 'N/A')}x",
                    err=True
                )
                click.echo(
                    f"    CO2 Impact: "
                    f"{issue.get('codebase_emissions', 0):.9f} kg",
                    err=True
                )
                click.echo(
                    f"    Effort to Fix: {issue.get('effort', 'Medium')}",
                    err=True
                )
                click.echo(
                    f"    Remediation: {issue.get('remediation', 'N/A')}",
                    err=True
                )
                if issue.get('ai_suggestion'):
                    click.echo(
                        f"    AI Suggestion: {issue.get('ai_suggestion')}",
                        err=True
                    )
                click.echo(
                    f"    Tags: {', '.join(issue.get('tags', []))}", err=True
                )

        # Handle fixing options
        if fix_all:
            click.echo("\nFixing all issues automatically...", err=True)
            # Group issues by file
            issues_by_file = {}
            for issue in results['issues']:
                file_path = issue.get('file')
                if file_path:
                    if file_path not in issues_by_file:
                        issues_by_file[file_path] = []
                    issues_by_file[file_path].append(issue)

            total_fixed = 0
            total_failed = 0

            for file_path, file_issues in issues_by_file.items():
                click.echo(f"  Processing {file_path}...", err=True)
                fix_result = scanner.remediation_engine.fix_file(
                    file_path, file_issues
                )
                fixed = fix_result.get('fixed', 0)
                failed = fix_result.get('failed', 0)
                total_fixed += fixed
                total_failed += failed

                if fixed > 0:
                    click.echo(f"    Fixed {fixed} issues.", err=True)
                if failed > 0:
                    click.echo(f"    Failed to fix {failed} issues.", err=True)

            click.echo(
                f"\nTotal: {total_fixed} fixed, {total_failed} failed.",
                err=True
            )

        elif fix_specific:
            click.echo(f"\nFixing specific issues: {fix_specific}", err=True)
            # Filter issues
            target_issues = [
                i for i in results['issues'] if i.get('id') in fix_specific
            ]

            if not target_issues:
                click.echo("No matching issues found.", err=True)
            else:
                issues_by_file = {}
                for issue in target_issues:
                    file_path = issue.get('file')
                    if file_path:
                        if file_path not in issues_by_file:
                            issues_by_file[file_path] = []
                        issues_by_file[file_path].append(issue)

                for file_path, file_issues in issues_by_file.items():
                    fix_result = scanner.remediation_engine.fix_file(
                        file_path, file_issues
                    )
                    fixed = fix_result.get('fixed', 0)
                    failed = fix_result.get('failed', 0)
                    click.echo(
                        f"  {file_path}: Fixed {fixed}, Failed {failed}",
                        err=True
                    )
        elif manual:
            click.echo(
                "\nManual mode: Review issues above and fix manually.",
                err=True
            )
        else:
            click.echo(
                "\nNo fixing option selected. Use --fix-all, --fix-specific, "
                "or --manual.",
                err=True
            )

        # Cleanup Git repo if cloned
        if cleanup_after and git_url:
            click.echo("\nCleaning up temporary repository...", err=True)
            GitOperations.cleanup_repo(scan_path)
            click.echo("[OK] Cleanup complete", err=True)

    except Exception as e:
        click.echo(f"Error during scan: {e}", err=True)
        sys.exit(1)
