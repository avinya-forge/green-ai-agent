import click
import sys
import os
import difflib
from typing import List, Optional
from src.core.scanner import Scanner
from src.core.config import ConfigLoader
from src.core.llm.factory import LLMFactory
from src.ui.state import set_last_scan_results

def extract_snippet(file_path: str, line_number: int, context_lines: int = 2) -> str:
    """
    Extract a code snippet around a specific line number.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start = max(0, line_number - 1 - context_lines)
        end = min(len(lines), line_number + context_lines)

        snippet = "".join(lines[start:end])
        return snippet
    except Exception:
        return ""

def print_diff(original: str, fixed: str):
    """
    Print a colored unified diff between original and fixed code.
    """
    original_lines = original.splitlines(keepends=True)
    fixed_lines = fixed.splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        fixed_lines,
        fromfile='Original',
        tofile='Fixed',
        lineterm=''
    )

    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            click.secho(line.rstrip(), fg='green')
        elif line.startswith('-') and not line.startswith('---'):
            click.secho(line.rstrip(), fg='red')
        elif line.startswith('^'):
            click.secho(line.rstrip(), fg='blue')
        else:
            click.echo(line.rstrip())

def apply_fix_to_file(file_path: str, original_snippet: str, fixed_snippet: str) -> bool:
    """
    Apply the fix to the file.
    Tries to locate the original snippet in the content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Normalize newlines for robust matching
        # Note: This might change line endings if we write back.
        # Ideally we preserve original line endings, but for now we prioritize functionality.
        content_norm = content.replace('\r\n', '\n')
        snippet_norm = original_snippet.replace('\r\n', '\n')
        fixed_norm = fixed_snippet.replace('\r\n', '\n')

        # Check if snippet exists
        count = content_norm.count(snippet_norm)

        if count == 0:
            click.secho("  Error: Could not locate original snippet in file (file might have changed).", fg='red')
            # Fallback: Try stripped match?
            return False

        if count == 1:
            # Unique match, safe to replace
            new_content = content_norm.replace(snippet_norm, fixed_norm)
        else:
            # Multiple matches.
            click.secho("  Warning: Multiple occurrences of snippet found. Skipping to avoid ambiguity.", fg='yellow')
            return False

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    except Exception as e:
        click.secho(f"  Error applying fix: {e}", fg='red')
        return False

def determine_language(file_path: str) -> str:
    """Determine language from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.py':
        return 'python'
    if ext == '.js':
        return 'javascript'
    if ext == '.ts':
        return 'typescript'
    if ext == '.java':
        return 'java'
    if ext == '.go':
        return 'go'
    return 'python' # Default

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True), required=False)
@click.option('--config', type=click.Path(exists=True), default=None, help='Path to .green-ai.yaml config file')
@click.option('--provider', default=None, help='LLM Provider (openai, mock)')
@click.option('--auto-apply', is_flag=True, help='Automatically apply fixes without confirmation')
@click.option('--verbose', is_flag=True, help='Show detailed output')
def fix_ai(paths, config, provider, auto_apply, verbose):
    """
    Scan and interactively fix green software violations using AI.
    """
    if not paths:
        # Check if running in a project with config that implies paths?
        # Scan command handles "no paths" by checking git-url.
        # Here we only support local paths for fixing.
        click.echo("Error: Please provide at least one path to scan/fix.", err=True)
        sys.exit(1)

    # Load configuration
    config_loader = ConfigLoader(config)
    cfg = config_loader.load()

    # Initialize Scanner
    # We default to python if not configured, but scanner handles multiple languages if paths provided?
    # Actually Scanner constructor takes `language`.
    # Ideally Scanner should auto-detect language per file or scan all enabled languages.
    # Current Scanner implementation seems to take one language argument.
    # Let's rely on config.
    enabled_languages = cfg.get('languages', ['python'])
    language = enabled_languages[0] # Primary language

    scanner = Scanner(language=language, config_path=config)

    click.echo(f"Scanning {', '.join(paths)}...")
    results = scanner.scan(list(paths))
    issues = results.get('issues', [])

    # Filter only green violations (skip errors)
    issues = [i for i in issues if i.get('type') == 'green_violation']

    if not issues:
        click.echo("No violations found. Great job!")
        return

    # Initialize LLM
    llm = LLMFactory.get_provider(provider, config=cfg)
    if not llm:
        click.echo("Error: Could not initialize LLM provider. Check API key or config.")
        sys.exit(1)

    click.echo(f"Found {len(issues)} violations.")
    click.echo(f"Starting AI fix process with {llm.__class__.__name__}...")

    # Check if dry run (mock provider implies dry run effectively, but we support writing for any provider)
    # The prompt said "PREVIEW mode. Fixes are simulated".
    # But user requested "Apply Fix".
    # We will remove the "PREVIEW" warning since we implemented apply logic.

    fixed_count = 0
    skipped_count = 0
    failed_count = 0

    for i, issue in enumerate(issues, 1):
        rule_id = issue.get('id')
        file_path = issue.get('file')
        line = issue.get('line')
        message = issue.get('message')

        # Determine language for this file
        file_lang = determine_language(file_path)

        click.echo(f"\n[{i}/{len(issues)}] Violation: {rule_id}")
        click.echo(f"  File: {file_path}:{line}")
        click.echo(f"  Message: {message}")

        snippet = extract_snippet(file_path, line)
        if not snippet:
            click.echo("  Warning: Could not read code snippet (or file access error).")
            skipped_count += 1
            continue

        click.echo("  Generating fix...")
        try:
            fix = llm.generate_fix(snippet, message, language=file_lang)
        except Exception as e:
            click.echo(f"  Error generating fix: {e}")
            failed_count += 1
            continue

        if not fix:
            click.echo("  No fix generated.")
            skipped_count += 1
            continue

        # Show Diff
        click.echo("-" * 40)
        click.echo("Proposed Fix (Diff):")
        print_diff(snippet, fix)
        click.echo("-" * 40)

        if auto_apply:
            apply = True
        else:
            apply = click.confirm("Apply this fix?")

        if apply:
            success = apply_fix_to_file(file_path, snippet, fix)
            if success:
                click.secho("  Fix applied successfully.", fg='green')
                fixed_count += 1
            else:
                click.secho("  Failed to apply fix.", fg='red')
                failed_count += 1
        else:
            click.echo("  Skipped.")
            skipped_count += 1

    # Report Usage
    usage = llm.get_total_usage()
    click.echo("\nProcess Complete.")
    click.echo(f"Fixed: {fixed_count}, Skipped: {skipped_count}, Failed: {failed_count}")
    click.echo(f"Token Usage: {usage.total_tokens} tokens")
    click.echo(f"Estimated Cost: ${usage.cost:.6f}")
