from pygls.lsp.server import LanguageServer
ls = LanguageServer("test", "v1")
print(hasattr(ls, 'window_log_message'))
try:
    ls.window_show_message("test")
except Exception as e:
    print(e)
