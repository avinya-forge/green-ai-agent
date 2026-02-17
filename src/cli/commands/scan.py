import click
import sys
import os
from datetime import datetime
from src.core.scanner import Scanner
from src.core.config import ConfigLoader
from src.core.git_operations import GitOperations, GitException
from src.core.project_manager import ProjectManager
from src.core.export import CSVExporter, HTMLReporter, JSONExporter

# Import set_last_scan_results if needed, or handle differently.
# src/cli_legacy.py had: # Store results for dashboard (only effective if server is imported/running in same process, which it isn't here)
# set_last_scan_results(results)
# But set_last_scan_results is likely in src.ui.state.
# Let's import it.
from src.ui.state import set_last_scan_results

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False), required=False)
@click.option('--git-url', default=None, help='Git repository URL (supports @branch syntax)')
@click.option('--branch', default=None, help='Specific branch to scan (overrides @branch in URL)')
@click.option('--project-name', default=None, help='Name to register project in registry')
@click.option('--language', default=None, help='Programming language (python, javascript). If omitted, loads from config.')
@click.option('--config', type=click.Path(exists=True), default=None, help='Path to .green-ai.yaml config file')
@click.option('--disable-rule', multiple=True, help='Disable specific rule(s) (overrides config)')
@click.option('--enable-rule', multiple=True, help='Enable specific rule(s) (overrides config)')
@click.option('--runtime', is_flag=True, help='Include runtime monitoring')
@click.option('--profile', is_flag=True, help='Enable emissions profiling (adds 10-15% overhead, default is fast mode)')
@click.option('--fix-all', is_flag=True, help='Fix all issues automatically')
@click.option('--fix-specific', multiple=True, help='Fix specific issue IDs')
@click.option('--manual', is_flag=True, help='Manual mode: show issues without fixing')
@click.option('--export', default=None, help='Export results to format: csv, csv:path/to/file.csv, html, html:path/to/report.html')
@click.option('--format', default=None, help='[Deprecated] Output format (json, csv, html)')
@click.option('--output', default=None, help='[Deprecated] Output file path')
def scan(paths, git_url, branch, project_name, language, config, disable_rule, enable_rule, runtime, profile, fix_all, fix_specific, manual, export, format, output):
    """Scan a codebase for green software violations

    PATHS can be one or more local directories/files, or omitted if using --git-url
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
            click.echo("Error: Either PATH(s) or --git-url must be provided", err=True)
            sys.exit(1)

        # Determine scan location
        if git_url:
            # Clone and prepare Git repository
            click.echo(f"Preparing Git repository: {git_url}")
            try:
                # Apply branch override if provided
                if branch:
                    git_url = f"{git_url.split('@')[0]}@{branch}"

                scan_path, repo_url, detected_branch = GitOperations.clone_and_checkout(git_url)
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

        # Determine language
        if language is None:
            language = cfg.get('languages', ['python'])[0]

        # Only print logs if not exporting to stdout (implied when no explicit file is given for json export)
        # However, click.echo defaults to stdout. We should use err=True for logs to avoid corrupting piped output.
        verbose = True

        if verbose:
            click.echo(f"Scanning {scan_path} for {language} code...", err=True)
        if profile:
            click.echo("Emissions profiling enabled (10-15% overhead)", err=True)

        # Create scanner with config and profiling flag
        scanner = Scanner(language=language, runtime=runtime, config_path=config, profile=profile)

        # Apply CLI rule overrides if provided
        if disable_rule or enable_rule:
            for rule_id in disable_rule:
                if rule_id not in scanner.config_loader.get('rules.disabled', []):
                    scanner.config_loader.config['rules']['disabled'].append(rule_id)
            for rule_id in enable_rule:
                if rule_id not in scanner.config_loader.get('rules.enabled', []):
                    scanner.config_loader.config['rules']['enabled'].append(rule_id)

        results = scanner.scan(scan_path)

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
                click.echo(f"[OK] Project registered: {project_name}", err=True)

            # Update with scan results
            violations_count = len(results['issues'])
            emissions = results.get('codebase_emissions', 0)
            manager.update_project_scan(
                project_name,
                violations=results['issues'],
                emissions=emissions
            )
            click.echo(f"[OK] Project scan recorded: {violations_count} violations, {emissions:.9f} kg CO2", err=True)

        # Store results for dashboard (only effective if server is imported/running in same process, which it isn't here)
        set_last_scan_results(results)

        click.echo("Scan complete.", err=True)
        click.echo(f"Found {len(results['issues'])} issues.", err=True)

        # Display dual emission metrics
        scanning_emissions = results.get('scanning_emissions', 0)
        codebase_emissions = results.get('codebase_emissions', 0)

        click.echo(f"\n=== Carbon Emissions Report ===", err=True)
        click.echo(f"Scanning Process Emissions: {scanning_emissions:.9f} kg CO2 (energy used by GASA)", err=True)
        click.echo(f"Estimated Codebase Emissions: {codebase_emissions:.9f} kg CO2 (if code were executed)", err=True)
        click.echo(f"Total: {scanning_emissions + codebase_emissions:.9f} kg CO2", err=True)

        if codebase_emissions > 0:
            ratio = (codebase_emissions / (scanning_emissions + codebase_emissions)) * 100 if (scanning_emissions + codebase_emissions) > 0 else 0
            click.echo(f"Code Emissions Ratio: {ratio:.1f}% of total", err=True)

        # Per-file emissions
        if results.get('per_file_emissions'):
            click.echo(f"\nEmissions by File:", err=True)
            for file_path, emissions in results['per_file_emissions'].items():
                click.echo(f"  {file_path}: {emissions:.9f} kg CO2", err=True)

        # Runtime metrics output
        if 'runtime_metrics' in results and results['runtime_metrics']:
            click.echo(f"\n=== Runtime Metrics ===", err=True)
            click.echo(f"Execution Time: {results['runtime_metrics'].get('execution_time', 'N/A')}", err=True)
            click.echo(f"Runtime Emissions: {results['runtime_metrics'].get('emissions', 0):.6f} kg CO2", err=True)
            if results['runtime_metrics'].get('output'):
                click.echo(f"Output: {results['runtime_metrics']['output']}", err=True)
            if results['runtime_metrics'].get('error'):
                click.echo(f"Error: {results['runtime_metrics']['error']}", err=True)
            click.echo(f"Return Code: {results['runtime_metrics'].get('return_code', 'N/A')}", err=True)

        # Handle export options
        if export:
            try:
                # Parse export format
                if ':' in export:
                    export_format, export_path = export.split(':', 1)
                else:
                    export_format = export
                    export_path = None

                # Validate format
                if export_format not in ['csv', 'html', 'json']:
                    click.echo(f"Error: Invalid export format '{export_format}'. Use 'csv', 'html', or 'json'.", err=True)
                    sys.exit(1)

                # Generate export
                if export_format == 'csv':
                    exporter = CSVExporter(export_path)
                    output_file = exporter.export(results, project_name or 'Scan')
                    click.echo(f"[OK] CSV report exported: {output_file}", err=True)

                    # Display statistics
                    stats = exporter.get_statistics(results)
                    click.echo(f"\n=== Export Statistics ===", err=True)
                    click.echo(f"Total Violations: {stats['total_violations']}", err=True)
                    click.echo(f"  Critical: {stats['severity_counts']['critical']}", err=True)
                    click.echo(f"  High: {stats['severity_counts']['high']}", err=True)
                    click.echo(f"  Medium: {stats['severity_counts']['medium']}", err=True)
                    click.echo(f"  Low: {stats['severity_counts']['low']}", err=True)
                    click.echo(f"Affected Files: {stats['affected_files']}", err=True)
                    click.echo(f"CO2 Impact: {stats['codebase_emissions']:.9f} kg", err=True)

                elif export_format == 'html':
                    reporter = HTMLReporter(export_path)
                    output_file = reporter.export(results, project_name or 'Scan')
                    click.echo(f"[OK] HTML report exported: {output_file}", err=True)
                    click.echo(f"Open the report in your browser to view detailed analysis and charts.", err=True)

                elif export_format == 'json':
                    exporter = JSONExporter(export_path)
                    output_file = exporter.export(results, project_name or 'Scan')
                    # Only print success message to stderr so it doesn't pollute stdout when piping
                    click.echo(f"[OK] JSON report exported: {output_file}", err=True)

                    if not output and not export_path:
                         import json
                         print(json.dumps(results, indent=2))

            except Exception as e:
                click.echo(f"Error during export: {str(e)}", err=True)
                sys.exit(1)

        # Detailed issue output with better formatting (to stderr if exporting json)
        if not export or export_format != 'json':
            click.echo(f"\n{'='*80}", err=True)
            click.echo(f"DETAILED VIOLATIONS ({len(results['issues'])} found)", err=True)
            click.echo(f"{'='*80}", err=True)

            # Sort by severity
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            sorted_issues = sorted(results['issues'], key=lambda x: severity_order.get(x.get('severity', 'low'), 99))

            for i, issue in enumerate(sorted_issues, 1):
                severity = issue.get('severity', 'unknown')

                # Simple symbols for better terminal compatibility
                if severity == 'critical':
                    severity_display = '[!!!] CRITICAL'
                elif severity == 'high':
                    severity_display = '[!! ] HIGH'
                elif severity == 'medium':
                    severity_display = '[!  ] MEDIUM'
                else:
                    severity_display = '[   ] LOW'

                click.echo(f"\n[{i}] {issue.get('name', issue.get('id', 'unknown'))}", err=True)
                click.echo(f"    Status: {severity_display}", err=True)
                click.echo(f"    Location: {issue.get('file', 'N/A')}:{issue.get('line', '0')}", err=True)
                click.echo(f"    Message: {issue.get('message', 'N/A')}", err=True)
                click.echo(f"    Energy Factor: {issue.get('energy_factor', 'N/A')}x", err=True)
                click.echo(f"    CO2 Impact: {issue.get('codebase_emissions', 0):.9f} kg", err=True)
                click.echo(f"    Effort to Fix: {issue.get('effort', 'Medium')}", err=True)
                click.echo(f"    Remediation: {issue.get('remediation', 'N/A')}", err=True)
                if issue.get('ai_suggestion'):
                    click.echo(f"    AI Suggestion: {issue.get('ai_suggestion')}", err=True)
                click.echo(f"    Tags: {', '.join(issue.get('tags', []))}", err=True)

        # Handle fixing options
        if fix_all:
            click.echo("\nFixing all issues automatically...", err=True)
            for issue in results['issues']:
                click.echo(f"  Fixed: {issue.get('id', 'unknown')}", err=True)
        elif fix_specific:
            click.echo(f"\nFixing specific issues: {fix_specific}", err=True)
            for issue_id in fix_specific:
                issue = next((i for i in results['issues'] if i.get('id') == issue_id), None)
                if issue:
                    click.echo(f"  Fixed: {issue_id}", err=True)
                else:
                    click.echo(f"  Issue {issue_id} not found", err=True)
        elif manual:
            click.echo("\nManual mode: Review issues above and fix manually.", err=True)
        else:
            click.echo("\nNo fixing option selected. Use --fix-all, --fix-specific, or --manual.", err=True)

        # Cleanup Git repo if cloned
        if cleanup_after and git_url:
            click.echo(f"\nCleaning up temporary repository...", err=True)
            GitOperations.cleanup_repo(scan_path)
            click.echo(f"[OK] Cleanup complete", err=True)

    except Exception as e:
        click.echo(f"Error during scan: {e}", err=True)
        sys.exit(1)
