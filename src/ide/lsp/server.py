import logging
from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    DidSaveTextDocumentParams,
    InitializeParams,
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
    TEXT_DOCUMENT_CODE_ACTION,
    CodeActionParams,
    CodeAction,
    CodeActionKind,
    WorkspaceEdit,
    TextEdit,
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
    msg = "Green AI LSP Initialized"
    logger.info(msg)
    ls.window_show_message(msg)
    return None


@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: GreenAILanguageServer, params: DidOpenTextDocumentParams):
    """Handle document open."""
    msg = f"Document opened: {params.text_document.uri}"
    logger.info(msg)
    ls.window_show_message(msg)
    _validate(ls, params)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: GreenAILanguageServer, params: DidChangeTextDocumentParams):
    """Handle document change."""
    _validate(ls, params)


@server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: GreenAILanguageServer, params: DidSaveTextDocumentParams):
    """Handle document save."""
    msg = f"Document saved: {params.text_document.uri}"
    logger.info(msg)
    ls.window_show_message(msg)
    _validate(ls, params)


@server.feature(TEXT_DOCUMENT_CODE_ACTION)
def code_action(ls: GreenAILanguageServer, params: CodeActionParams):
    """Handle code action requests (quick fixes)."""
    items = []

    for diagnostic in params.context.diagnostics:
        if "Avoid using print() in production" in diagnostic.message:
            # Provide quick fix to replace print( with logger.info(
            edit = TextEdit(range=diagnostic.range, new_text="logger.info(")
            workspace_edit = WorkspaceEdit(changes={params.text_document.uri: [edit]})
            action = CodeAction(
                title="Replace with logger.info(",
                kind=CodeActionKind.QuickFix,
                diagnostics=[diagnostic],
                edit=workspace_edit,
            )
            items.append(action)

    return items


def main():
    server.start_io()


if __name__ == '__main__':
    main()
