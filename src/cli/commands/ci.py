import click
import sys
import os
from src.core.ci.github_client import GitHubClient

@click.group()
def ci():
    """CI/CD Integration commands."""
    pass

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
