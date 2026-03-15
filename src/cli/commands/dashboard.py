import click
import logging
from pathlib import Path


@click.command()
def dashboard():
    """Launch the web dashboard"""
    # Import server here to avoid eventlet monkey patching during other commands
    try:
        from src.ui.server import run_dashboard
    except ImportError as e:
        click.echo(f"Error importing dashboard server: {e}", err=True)
        return

    # Configure Flask logging to output/logs
    # Note: Using absolute path resolution relative to this file
    # This file is src/cli/commands/dashboard.py
    # output is src/../output
    logs_dir = Path(__file__).parent.parent.parent.parent / 'output' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'server.log'),
            logging.StreamHandler()
        ]
    )

    click.echo("Launching dashboard at http://localhost:5000")
    click.echo(f"Logs will be saved to: {logs_dir}")
    run_dashboard()
