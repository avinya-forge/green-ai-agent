"""
CLI command to initialize configuration.
"""

import click
import yaml
from pathlib import Path
from src.core.config import ConfigLoader

@click.command()
@click.option('--path', default='.', help='Directory to initialize config in.')
def init(path):
    """Initialize a new Green-AI configuration."""
    target_dir = Path(path)
    target_path = target_dir / '.green-ai.yaml'

    if target_path.exists():
        click.echo(f"Configuration file already exists at {target_path}")
        if not click.confirm("Do you want to overwrite it?"):
            return

    # Create directory if not exists
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    # Use default config from ConfigLoader which has the enabled rules list
    config = ConfigLoader.DEFAULT_CONFIG.copy()

    # Dump to yaml
    try:
        with open(target_path, 'w') as f:
            f.write("# Green-AI Configuration\n")
            f.write("# Generated via 'green-ai init'\n")
            f.write("# Customize this file to configure rules, languages, and thresholds.\n\n")
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        click.echo(f"✅ Initialized configuration at {target_path}")
    except Exception as e:
        click.echo(f"❌ Failed to create configuration: {e}", err=True)
