import click
from src.ide.lsp.server import server

@click.command(name="lsp")
@click.option("--tcp", is_flag=True, help="Use TCP server instead of standard I/O")
@click.option("--host", default="127.0.0.1", help="Bind address for TCP server")
@click.option("--port", default=2087, help="Bind port for TCP server")
def lsp(tcp, host, port):
    """Start the Green-AI Language Server Protocol (LSP) server."""
    if tcp:
        click.echo(f"Starting Green-AI LSP server on tcp://{host}:{port}")
        server.start_tcp(host, port)
    else:
        server.start_io()
