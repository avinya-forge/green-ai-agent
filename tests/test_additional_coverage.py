import pytest
from src.core.scanner.suppression import is_suppressed, get_suppressions, load_external_suppressions
from src.core.scanner.worker import _checks_include, scan_file_worker
from unittest.mock import patch, mock_open

def test_checks_include_variations():
    assert _checks_include({'checks': 'energy'}, 'energy') is True
    assert _checks_include({'checks': ['energy', 'ai']}, 'ai') is True
    assert _checks_include({}, 'energy') is True
    assert _checks_include({}, 'ai') is False

def test_is_suppressed_edge_cases():
    issue = {'id': 'rule1', 'file': 'test.py', 'line': 10}
    # Global suppression
    assert is_suppressed(issue, {}, {'*': ['rule1']}) is True
    # File asterisk suppression
    assert is_suppressed(issue, {}, {'test.py': ['*']}) is True
    # Not suppressed
    assert is_suppressed(issue, {}, {'other.py': ['rule1']}) is False
    # Inline list format
    assert is_suppressed(issue, [10], {}) is True

def test_load_external_suppressions_malformed(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("!!binary 'garbage'")
    assert load_external_suppressions(str(p)) == {}

def test_worker_syntax_error_handling(tmp_path):
    p = tmp_path / "syntax.py"
    p.write_text("def foo(")
    result = scan_file_worker(str(p), 'python', {}, [])
    assert any(i['id'] == 'syntax_error' for i in result['issues'])

def test_worker_exception_handling():
    # Force an exception during file read
    with patch('builtins.open', side_effect=Exception("Read error")):
        result = scan_file_worker('nonexistent.py', 'python', {}, [])
        assert any(i['id'] == 'parse_error' for i in result['issues'])
