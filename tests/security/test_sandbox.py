import pytest
from src.core.security.llm_guard import check_code_safety

class TestCodeSafety:
    def test_safe_python_code(self):
        code = "print('Hello, world!')"
        warnings = check_code_safety(code, 'python')
        assert len(warnings) == 0

    def test_risky_python_imports(self):
        code = "import os\nos.system('rm -rf /')"
        warnings = check_code_safety(code, 'python')
        assert any("Import of 'os'" in w for w in warnings)
        assert any("Usage of 'os.system'" in w for w in warnings)

    def test_risky_python_builtins(self):
        code = "eval('print(1)')"
        warnings = check_code_safety(code, 'python')
        assert any("Usage of 'eval'" in w for w in warnings)

    def test_risky_python_wrapped(self):
        # Indentation should be handled
        code = "  import subprocess\n  subprocess.call(['ls'])"
        warnings = check_code_safety(code, 'python')
        assert any("Import of 'subprocess'" in w for w in warnings)

    def test_risky_js_code(self):
        code = "eval('alert(1)')"
        warnings = check_code_safety(code, 'javascript')
        assert any("Usage of 'eval'" in w for w in warnings)

    def test_risky_js_process(self):
        code = "process.exit(1)"
        warnings = check_code_safety(code, 'javascript')
        assert any("Usage of 'process.exit'" in w for w in warnings)

    def test_safe_js_code(self):
        code = "console.log('Hello')"
        warnings = check_code_safety(code, 'javascript')
        assert len(warnings) == 0

    def test_obfuscated_python_keyword(self):
        # If parsing fails, it falls back to keyword search
        code_fragment = "This is not valid python code but contains eval( bad stuff"
        warnings = check_code_safety(code_fragment, 'python')

        # It should warn about eval(
        assert any("eval(" in w for w in warnings) or any("Usage of 'eval'" in w for w in warnings)
