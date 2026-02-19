import pytest
import textwrap
from src.core.remediation.strategies.python import ListAppendToComprehension
from src.core.remediation.engine import RemediationEngine

def test_apply_fix_list_comprehension():
    """Test applying fix for list comprehension."""
    code = textwrap.dedent("""
    def process(items):
        result = []
        for item in items:
            result.append(item)
        return result
    """).strip()

    # Line 1: def process...
    # Line 2: result = []
    # Line 3: for item in items:

    strategy = ListAppendToComprehension()
    fixed_code = strategy.apply_fix(code, 3)

    assert fixed_code is not None
    # LibCST usually maintains indentation
    assert "result.extend([item for item in items])" in fixed_code

def test_remediation_engine_fix_file(tmp_path):
    """Test RemediationEngine.fix_file."""
    f = tmp_path / "fix_test.py"
    original_content = textwrap.dedent("""
    def test():
        l = []
        for i in range(10):
            l.append(i)
    """).strip()

    f.write_text(original_content, encoding='utf-8')

    engine = RemediationEngine()

    # Line 1: def test():
    # Line 2: l = []
    # Line 3: for i in range(10):

    violations = [{
        'id': 'inefficient_loop',
        'line': 3,
        'file': str(f)
    }]

    result = engine.fix_file(str(f), violations)

    assert result['fixed'] == 1, f"Failed: {result}"
    assert result['failed'] == 0

    new_content = f.read_text(encoding='utf-8')
    assert "l.extend([i for i in range(10)])" in new_content
