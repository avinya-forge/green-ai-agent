import sys
import click
from src.standards.registry import StandardsRegistry
from src.standards.sync_engine import StandardsSyncEngine, _STALE_THRESHOLD_DAYS


@click.group()
def standards():
    """Manage green coding standards"""


@standards.command('list')
def standards_list():
    """List all available standards"""
    registry = StandardsRegistry()
    standards_info = registry.list_standards()

    click.echo("\n=== Available Green Coding Standards ===\n")
    for name, info in standards_info.items():
        status = "[ENABLED]" if info['enabled'] else "[DISABLED]"
        click.echo(f"{name.upper()} {status}")
        click.echo(f"  Rules: {info['rule_count']}")
        click.echo(f"  Languages: {', '.join(info['languages'])}")
        click.echo()


@standards.command('enable')
@click.argument('standard_name')
def standards_enable(standard_name):
    """Enable a standard"""
    registry = StandardsRegistry()
    registry.enable_standard(standard_name)
    click.echo(f"[OK] Standard '{standard_name}' enabled")


@standards.command('disable')
@click.argument('standard_name')
def standards_disable(standard_name):
    """Disable a standard"""
    registry = StandardsRegistry()
    registry.disable_standard(standard_name)
    click.echo(f"[OK] Standard '{standard_name}' disabled")


@standards.command('update')
def standards_update():
    """Sync standards from online sources (legacy alias for 'sync')"""
    registry = StandardsRegistry()
    result = registry.sync_standards()
    click.echo("[OK] Standards updated from online sources")
    for standard, status in result.items():
        click.echo(f"  {standard}: {'[OK]' if status else '[X]'}")


@standards.command('export')
@click.option('--format', type=click.Choice(['json', 'yaml']), default='json', help='Export format')
def standards_export(format):
    """Export enabled rules"""
    registry = StandardsRegistry()
    if format == 'json':
        output = registry.export_rules_json()
    else:
        output = registry.export_rules_yaml()
    click.echo(output)


# ── EPIC-29: Standards Sync Engine commands ───────────────────────────────────

@standards.command('sync')
@click.option('--source', default=None, help='Sync a specific source (gsf|ecocode|owasp|cwe|epss)')
@click.option('--force', is_flag=True, default=False, help='Force sync even if cache is fresh')
@click.option('--interval', default=24, type=int, show_default=True,
              help='Sync interval in hours (controls cache freshness)')
def standards_sync(source, force, interval):
    """
    Sync live standards from remote sources.

    Sources: gsf, ecocode, owasp, cwe, epss

    Fetched content is cached locally with SHA-256 hash verification.
    Re-sync is skipped if the cache is fresher than --interval hours.
    Use --force to bypass the interval check.
    """
    engine = StandardsSyncEngine(sync_interval_hours=interval)

    if source:
        try:
            entry = engine.sync_source(source, force=force)
        except ValueError as exc:
            click.echo(f"[ERROR] {exc}", err=True)
            sys.exit(1)
        _print_sync_entry(entry)
    else:
        results = engine.sync_all(force=force)
        click.echo("\n=== Standards Sync Results ===\n")
        for entry in results.values():
            _print_sync_entry(entry)

    click.echo()
    click.echo("Run 'green-ai standards versions' to see manifest details.")


def _print_sync_entry(entry) -> None:
    status = "[OK]" if entry.sync_ok else "[FAIL]"
    click.echo(f"  {status} {entry.display_name}")
    if entry.sync_ok:
        click.echo(f"       version : {entry.version_tag}")
        click.echo(f"       hash    : {entry.content_hash[:16]}…" if entry.content_hash else "")
        click.echo(f"       size    : {entry.size_bytes:,} bytes")
        click.echo(f"       synced  : {entry.last_sync}")
    else:
        click.echo(f"       error   : {entry.error}")


@standards.command('versions')
def standards_versions():
    """
    Show version manifest for all synced standards.

    Displays last sync timestamp, content hash, and size for each source.
    """
    engine = StandardsSyncEngine()
    rows = engine.versions()

    click.echo("\n=== Standards Version Manifest ===\n")
    click.echo(f"{'Source':<12} {'Display Name':<42} {'Version':<12} {'Hash':<16} {'OK':<6} {'Last Sync'}")
    click.echo("-" * 110)
    for row in rows:
        ok = "YES" if row['sync_ok'] else "NO"
        version = row['version_tag'] or "—"
        h = row['content_hash'] or "—"
        last = row['last_sync'] or "never"
        click.echo(
            f"{row['name']:<12} {row['display_name']:<42} {version:<12} {h:<16} {ok:<6} {last}"
        )
    click.echo()


@standards.command('check')
@click.option('--max-age-days', default=_STALE_THRESHOLD_DAYS, type=int, show_default=True,
              help='Maximum age in days before a source is considered stale')
@click.option('--fail-on-stale', is_flag=True, default=False,
              help='Exit with code 1 if any source is stale (for CI gates)')
def standards_check(max_age_days, fail_on_stale):
    """
    Check whether synced standards are up to date.

    Use --fail-on-stale in CI pipelines to gate builds on fresh standards.
    Exit code 1 when stale sources are found and --fail-on-stale is set.

    Example (CI):
      green-ai standards check --max-age-days 7 --fail-on-stale
    """
    engine = StandardsSyncEngine()
    stale_map = engine.check_stale(max_age_days=max_age_days)

    click.echo(f"\n=== Standards Freshness Check (max age: {max_age_days} days) ===\n")
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
        click.echo("[!] Some standards are stale. Run: green-ai standards sync")
        if fail_on_stale:
            sys.exit(1)
    else:
        click.echo("[OK] All standards are fresh.")
