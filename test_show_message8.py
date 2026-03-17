from pygls.lsp.server import LanguageServer
ls = LanguageServer("test", "v1")
print(hasattr(ls, 'show_message_log'))
