#!/usr/bin/env python3
"""
Green-AI Agent — CLI tool.
"""

import click

from src.cli.commands.scan import scan
from src.cli.commands.project import project
from src.cli.commands.dashboard import dashboard
from src.cli.commands.standards import standards
from src.cli.commands.calibrate import calibrate
from src.cli.commands.fix_ai import fix_ai
from src.cli.commands.init import init
from src.cli.commands.ci import ci
from src.cli.commands.lsp import lsp


@click.group()
def cli():
    """Green-AI Agent."""


cli.add_command(scan)
cli.add_command(project)
cli.add_command(dashboard)
cli.add_command(standards)
cli.add_command(calibrate)
cli.add_command(fix_ai)
cli.add_command(init)
cli.add_command(ci)
cli.add_command(lsp)


if __name__ == "__main__":
    cli()
