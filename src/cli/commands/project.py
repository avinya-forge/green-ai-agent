import click
import sys
from src.core.project_manager import ProjectManager
from src.core.git_operations import GitOperations, GitException
from src.core.scanner import Scanner
from src.ui.state import set_last_scan_results


@click.group()
def project():
    """Manage projects in registry"""
    pass


@project.command('add')
@click.argument('name')
@click.argument('repo_url')
@click.option('--branch', default=None, help='Git branch (auto-detected if omitted)')
@click.option('--language', default='python', help='Programming language')
def project_add(name, repo_url, branch, language):
    """Add a new project to the registry

    NAME: Project name
    REPO_URL: Git URL or local path
    """
    try:
        manager = ProjectManager()

        # Check if project already exists
        if manager.get_project(name):
            click.echo(f"Error: Project '{name}' already exists", err=True)
            sys.exit(1)

        # Add project
        project = manager.add_project(
            name=name,
            repo_url=repo_url,
            branch=branch,
            language=language
        )

        click.echo(f"[OK] Project added: {name}")
        click.echo(f"  URL: {repo_url}")
        click.echo(f"  Branch: {project.branch or 'auto-detect'}")
        click.echo(f"  Language: {language}")
        click.echo(f"  ID: {project.id}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('list')
@click.option('--sort-by', type=click.Choice(['name', 'violations', 'last_scan', 'emissions', 'grade']),
              default='name', help='Sort projects by field')
def project_list(sort_by):
    """List all registered projects"""
    try:
        manager = ProjectManager()
        projects = manager.list_projects(sort_by=sort_by)

        if not projects:
            click.echo("No projects registered yet.")
            return

        click.echo(f"\n{'=' * 100}")
        click.echo(f"REGISTERED PROJECTS (sorted by {sort_by})")
        click.echo(f"{'=' * 100}\n")

        # Header
        click.echo(f"{'Name':<25} {'Language':<12} {'Grade':<7} {'Violations':<12} {'Last Scan':<20} {'Emissions':<15}")
        click.echo(f"{'-' * 25} {'-' * 12} {'-' * 7} {'-' * 12} {'-' * 20} {'-' * 15}")

        for p in projects:
            grade = p.get_grade()
            grade_symbol = {'A': '[A]', 'B': '[B]', 'C': '[C]', 'D': '[D]', 'F': '[F]'}.get(grade, '[ ]')

            last_scan = p.last_scan.split('T')[0] if p.last_scan else 'Never'

            click.echo(f"{p.name:<25} {p.language:<12} {grade_symbol} {grade:<5} {p.latest_violations:<12} {last_scan:<20} {p.total_emissions:.9f}")

        click.echo(f"\n{'=' * 100}")

        # Summary metrics
        metrics = manager.get_summary_metrics()
        click.echo("\nSummary:")
        click.echo(f"  Total Projects: {metrics['total_projects']}")
        click.echo(f"  Total Violations: {metrics['total_violations']}")
        click.echo(f"  Average Violations: {metrics['average_violations']:.1f}")
        click.echo(f"  Total Scans: {metrics['total_scans']}")
        click.echo(f"  Total Emissions: {metrics['total_emissions']:.9f} kg CO2")
        click.echo(f"  Average Grade: {metrics['average_grade']}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('remove')
@click.argument('name')
@click.confirmation_option(prompt='Are you sure you want to remove this project?')
def project_remove(name):
    """Remove a project from the registry"""
    try:
        manager = ProjectManager()

        if not manager.remove_project(name):
            click.echo(f"Error: Project '{name}' not found", err=True)
            sys.exit(1)

        click.echo(f"[OK] Project removed: {name}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('scan')
@click.argument('project_name')
@click.option('--branch', default=None, help='Override registered branch')
def project_scan(project_name, branch):
    """Scan a specific project from registry"""
    try:
        manager = ProjectManager()
        project = manager.get_project(project_name)

        if not project:
            click.echo(f"Error: Project '{project_name}' not found", err=True)
            sys.exit(1)

        # Prepare scan location
        repo_url = project.repo_url
        branch_to_use = branch or project.branch

        click.echo(f"Scanning project: {project_name}")
        click.echo(f"Repository: {repo_url}")

        # Use detect_and_prepare_repository to handle both Git URLs and local paths
        try:
            if GitOperations.is_git_url(repo_url):
                if branch_to_use:
                    repo_url_with_branch = f"{repo_url.split('@')[0]}@{branch_to_use}"
                else:
                    repo_url_with_branch = repo_url

                scan_path, _, detected_branch = GitOperations.clone_and_checkout(repo_url_with_branch)
                click.echo(f"✓ Repository cloned, branch: {detected_branch}")
                cleanup_after = True
            else:
                scan_path = repo_url
                cleanup_after = False
                click.echo("✓ Using local repository")

        except GitException as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        # Scan the repository
        try:
            scanner = Scanner(language=project.language, runtime=False, config_path=None)
            results = scanner.scan(scan_path)

            # Update project with scan results
            violations_count = len(results['issues'])
            emissions = results.get('codebase_emissions', 0)
            manager.update_project_scan(project_name, violations=results['issues'], emissions=emissions)

            click.echo("[OK] Scan complete")
            click.echo(f"  Found {violations_count} violations")
            click.echo(f"  Emissions: {emissions:.9f} kg CO2")
            click.echo(f"  Grade: {manager.get_project(project_name).get_grade()}")

            # Store for dashboard
            set_last_scan_results(results)

        finally:
            # Cleanup if needed
            if cleanup_after and GitOperations.is_git_url(repo_url):
                GitOperations.cleanup_repo(scan_path)
                click.echo("[OK] Cleaned up temporary repository")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('scan-all')
def project_scan_all():
    """Scan all registered projects"""
    try:
        manager = ProjectManager()
        projects = manager.list_projects()

        if not projects:
            click.echo("No projects to scan.")
            return

        click.echo(f"\nScanning {len(projects)} projects...\n")

        results_summary = []

        for i, project in enumerate(projects, 1):
            click.echo(f"[{i}/{len(projects)}] Scanning: {project.name}")

            try:
                # Prepare scan location
                repo_url = project.repo_url

                if GitOperations.is_git_url(repo_url):
                    scan_path, _, detected_branch = GitOperations.clone_and_checkout(repo_url)
                    cleanup_after = True
                else:
                    scan_path = repo_url
                    cleanup_after = False

                # Scan
                scanner = Scanner(language=project.language, runtime=False, config_path=None)
                results = scanner.scan(scan_path)

                # Update project
                violations_count = len(results['issues'])
                emissions = results.get('codebase_emissions', 0)
                manager.update_project_scan(project.name, violations=results['issues'], emissions=emissions)

                updated_project = manager.get_project(project.name)
                grade = updated_project.get_grade()

                click.echo(f"  [OK] {violations_count} violations, Grade: {grade}, Emissions: {emissions:.9f} kg CO2")
                results_summary.append((project.name, grade, violations_count, emissions))

                # Cleanup
                if cleanup_after:
                    GitOperations.cleanup_repo(scan_path)

            except Exception as e:
                click.echo(f"  ✗ Error: {e}")
                results_summary.append((project.name, 'ERROR', -1, 0))

        # Summary
        click.echo(f"\n{'=' * 80}")
        click.echo("SCAN RESULTS SUMMARY")
        click.echo(f"{'=' * 80}\n")

        for name, grade, violations, emissions in results_summary:
            grade_symbol = {'A': '[A]', 'B': '[B]', 'C': '[C]', 'D': '[D]', 'F': '[F]', 'ERROR': '[X]'}.get(grade, '[ ]')
            click.echo(f"{grade_symbol} {name:<30} Grade: {grade:<5} Violations: {violations:<4} Emissions: {emissions:.9f}")

        # Aggregate metrics
        metrics = manager.get_summary_metrics()
        click.echo(f"\n{'=' * 80}")
        click.echo("Aggregate Metrics:")
        click.echo(f"  Total Projects: {metrics['total_projects']}")
        click.echo(f"  Total Violations: {metrics['total_violations']}")
        click.echo(f"  Average Violations: {metrics['average_violations']:.1f}")
        click.echo(f"  Total Emissions: {metrics['total_emissions']:.9f} kg CO2")
        click.echo(f"  Average Grade: {metrics['average_grade']}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('export')
def project_export():
    """Export all projects as JSON"""
    try:
        manager = ProjectManager()
        json_output = manager.export_projects()
        click.echo(json_output)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
