import pytest
from src.core.detectors import detect_violations

def test_python_empty_loop():
    code = """
def process():
    for i in range(10):
        pass
    while True:
        ...
"""
    violations = detect_violations(code, "test.py", "python")

    assert any(v['id'] == 'empty_block' for v in violations)
    assert len([v for v in violations if v['id'] == 'empty_block']) == 2

def test_python_empty_if():
    code = """
if condition:
    pass
"""
    violations = detect_violations(code, "test.py", "python")

    assert any(v['id'] == 'empty_block' for v in violations)

def test_python_empty_func_class():
    code = """
def empty_func():
    pass

class EmptyClass:
    ...
"""
    violations = detect_violations(code, "test.py", "python")
    empty_blocks = [v for v in violations if v['id'] == 'empty_block']

    assert len(empty_blocks) == 2
    assert any("function" in v['message'] for v in empty_blocks)
    assert any("class" in v['message'] for v in empty_blocks)

def test_js_empty_block():
    code = """
function test() {
    if (x) {
        // empty
    }
    while(true) {}
}
"""
    violations = detect_violations(code, "test.js", "javascript")

    # Tree-sitter query should catch {}
    assert any(v['id'] == 'empty_block' for v in violations)
