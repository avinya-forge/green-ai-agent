import click
import sys
import json
from src.core.ci.github_client import GitHubClient
from src.core.ci.reporter import CIReporter
from src.standards.sync_engine import StandardsSyncEngine, _STALE_THRESHOLD_DAYS


@click.group()
def ci():
    """CI/CD Integration commands."""


@ci.command()
@click.option('--repo', required=True, help='Repository in format owner/repo')
@click.option('--pr', required=True, type=int, help='Pull Request Number')
@click.option('--body', help='Comment body text')
@click.option('--file', type=click.Path(exists=True), help='Read comment body from file')
def comment(repo, pr, body, file):
    """Post a comment to a GitHub Pull Request."""
    if not body and not file:
        click.echo("Error: Either --body or --file must be provided.", err=True)
        sys.exit(1)

    if body and file:
        click.echo("Error: Cannot provide both --body and --file.", err=True)
        sys.exit(1)

    comment_body = body
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                comment_body = f.read()
        except Exception as e:
            click.echo(f"Error reading file: {e}", err=True)
            sys.exit(1)

    try:
        owner, repo_name = repo.split('/')
    except ValueError:
        click.echo("Error: Repo must be in format owner/repo", err=True)
        sys.exit(1)

    try:
        client = GitHubClient()
        client.post_comment(owner, repo_name, pr, comment_body)
        click.echo(f"Successfully posted comment to PR #{pr} in {repo}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Failed to post comment: {e}", err=True)
        sys.exit(1)


@ci.command()
@click.option('--scan-results', required=True, type=click.Path(exists=True), help='Path to scan results JSON file')
@click.option('--repo', required=True, help='Repository in format owner/repo')
@click.option('--pr', required=True, type=int, help='Pull Request Number')
@click.option('--token', help='GitHub Token (optional, defaults to GITHUB_TOKEN env var)')
@click.option('--filter-diff', is_flag=True, help='Only report issues on changed lines')
def report(scan_results, repo, pr, token, filter_diff):
    """Post a scan report to a GitHub Pull Request."""
    try:
        with open(scan_results, 'r') as f:
            results = json.load(f)
    except Exception as e:
        click.echo(f"Error reading scan results: {e}", err=True)
        sys.exit(1)

    try:
        owner, repo_name = repo.split('/')
    except ValueError:
        click.echo("Error: Repo must be in format owner/repo", err=True)
        sys.exit(1)

    try:
        client = GitHubClient(token=token)

        diff_changes = None
        if filter_diff:
            click.echo(f"Fetching diff for PR #{pr}...", err=True)
            diff_text = client.get_pr_diff(owner, repo_name, pr)
            diff_changes = client.parse_diff(diff_text)
            click.echo(f"Parsed diff: {len(diff_changes)} changed files.", err=True)

        reporter = CIReporter()
        markdown_report = reporter.generate_report(results, diff_changes)

        click.echo("Posting report comment...", err=True)
        client.post_comment(owner, repo_name, pr, markdown_report)
        click.echo(f"Successfully posted report to PR #{pr} in {repo}")

    except Exception as e:
        click.echo(f"Failed to post report: {e}", err=True)
        sys.exit(1)


@ci.command('check-standards')
@click.option(
    '--max-age-days', default=_STALE_THRESHOLD_DAYS, type=int, show_default=True,
    help='Maximum age in days before a standards source is stale.'
)
@click.option(
    '--fail-on-stale', is_flag=True, default=False,
    help='Exit with code 2 if any source is stale (for CI gates).'
)
def ci_check_standards(max_age_days, fail_on_stale):
    """Check that synced standards are within the freshness threshold.

    Designed for CI pipelines — pair with --fail-on-stale to gate builds
    on fresh standards:

    \b
      green-ai ci check-standards --max-age-days 7 --fail-on-stale

    Exit codes:
      0  All sources fresh
      2  One or more sources stale (only when --fail-on-stale set)
    """
    engine = StandardsSyncEngine()
    stale_map = engine.check_stale(max_age_days=max_age_days)

    click.echo(
        f"\n=== Standards Freshness (max age: {max_age_days} days) ===\n"
    )
    any_stale = False
    for name, is_stale in stale_map.items():
        entry = engine.manifest.entries.get(name)
        last = entry.last_sync if entry and entry.last_sync else "never"
        flag = "[STALE]" if is_stale else "[OK]   "
        if is_stale:
            any_stale = True
        click.echo(f"  {flag} {name:<12} last synced: {last}")

    click.echo()
    if any_stale:
        click.echo(
            "[!] Stale standards detected. Run: green-ai standards sync",
            err=True
        )
        if fail_on_stale:
            sys.exit(2)
    else:
        click.echo("[OK] All standards are within the freshness threshold.")
