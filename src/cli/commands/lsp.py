import click
from src.ide.lsp.server import server


@click.command()
@click.option('--tcp', is_flag=True, help='Run the LSP server over TCP.')
@click.option('--host', default='127.0.0.1', help='Host to bind to when running over TCP.')
@click.option('--port', default=2087, type=int, help='Port to bind to when running over TCP.')
def lsp(tcp, host, port):
    """Start the Green AI Language Server."""
    if tcp:
        click.echo(f"Starting Green AI LSP server on tcp://{host}:{port}", err=True)
        server.start_tcp(host, port)
    else:
        # Defaults to standard I/O
        click.echo("Starting Green AI LSP server on stdio", err=True)
        server.start_io()
