#!/usr/bin/env python3
"""
Green AI Software Analyzer (GASA) - CLI Tool
"""

import click
import sys
import os

@click.group()
def cli():
    """Green AI Software Analyzer"""
    pass

# Register commands
try:
    from src.cli.commands.scan import scan
    cli.add_command(scan)

    from src.cli.commands.project import project
    cli.add_command(project)

    from src.cli.commands.dashboard import dashboard
    cli.add_command(dashboard)

    from src.cli.commands.standards import standards
    cli.add_command(standards)

    from src.cli.commands.calibrate import calibrate
    cli.add_command(calibrate)

    from src.cli.commands.fix_ai import fix_ai
    cli.add_command(fix_ai)

    from src.cli.commands.init import init
    cli.add_command(init)

    from src.cli.commands.ci import ci
    cli.add_command(ci)

except ImportError as e:
    # Fail fast during development
    raise e

if __name__ == "__main__":
    cli()
