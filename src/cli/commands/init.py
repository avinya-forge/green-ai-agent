"""
CLI command to initialize configuration.
"""

import click
import yaml
import shutil
import os
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

    # Try to copy from template
    # Assuming init.py is in src/cli/commands/
    template_path = Path(__file__).parent.parent / 'templates' / 'default_config.yaml'

    try:
        if template_path.exists():
             shutil.copy(template_path, target_path)
        else:
            # Fallback to ConfigLoader defaults if template is missing
            config = ConfigLoader.DEFAULT_CONFIG.copy()
            with open(target_path, 'w') as f:
                f.write("# Green-AI Configuration\n")
                f.write("# Generated via 'green-ai init'\n")
                f.write("# Customize this file to configure rules, languages, and thresholds.\n\n")
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        click.echo(f"✅ Initialized configuration at {target_path}")
    except Exception as e:
        click.echo(f"❌ Failed to create configuration: {e}", err=True)
