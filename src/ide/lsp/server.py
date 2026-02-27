import logging
import asyncio
from typing import Optional
from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_document_did_open,
    TEXT_document_did_change,
    TEXT_document_did_save,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    DidSaveTextDocumentParams,
    InitializeParams,
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
    PublishDiagnosticsParams,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GreenAILSP")

class GreenAILanguageServer(LanguageServer):
    def __init__(self):
        super().__init__("green-ai-lsp", "v0.1.0")

server = GreenAILanguageServer()

def _validate(ls: GreenAILanguageServer, params):
    """
    Validate the document and publish diagnostics.
    Mock implementation until Scanner is fully integrated.
    """
    text_doc = ls.workspace.get_text_document(params.text_document.uri)

    source = text_doc.source
    diagnostics = []

    # Mock check: Detect "print(" usage as a green violation
    for i, line in enumerate(source.splitlines()):
        if "print(" in line:
            start_char = line.find("print(")
            end_char = start_char + 6
            range_ = Range(
                start=Position(line=i, character=start_char),
                end=Position(line=i, character=end_char),
            )
            msg = "Avoid using print() in production. Use a logger instead."
            d = Diagnostic(
                range=range_,
                message=msg,
                severity=DiagnosticSeverity.Warning,
                source="Green-AI",
            )
            diagnostics.append(d)

    ls.publish_diagnostics(text_doc.uri, diagnostics)

@server.feature("initialize")
def initialize(ls: GreenAILanguageServer, params: InitializeParams):
    """Handle initialize request."""
    logger.info("Green AI LSP Initialized")
    return None

@server.feature(TEXT_document_did_open)
async def did_open(ls: GreenAILanguageServer, params: DidOpenTextDocumentParams):
    """Handle document open."""
    logger.info(f"Document opened: {params.text_document.uri}")
    _validate(ls, params)

@server.feature(TEXT_document_did_change)
async def did_change(ls: GreenAILanguageServer, params: DidChangeTextDocumentParams):
    """Handle document change."""
    _validate(ls, params)

@server.feature(TEXT_document_did_save)
async def did_save(ls: GreenAILanguageServer, params: DidSaveTextDocumentParams):
    """Handle document save."""
    logger.info(f"Document saved: {params.text_document.uri}")
    _validate(ls, params)

def main():
    server.start_io()

if __name__ == '__main__':
    main()
