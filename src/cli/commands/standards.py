import click
from src.standards.registry import StandardsRegistry

@click.group()
def standards():
    """Manage green coding standards"""
    pass


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
    """Sync standards from online sources"""
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
