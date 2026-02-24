import pytest
import ast
from src.core.detectors.python_detector import PythonViolationDetector

def detect_violations(code):
    detector = PythonViolationDetector(code, "test.py")
    detector.visit(ast.parse(code))
    return detector.violations

def test_entropy_in_assignment():
    # Simple assignment (already supported)
    code = 'secret = "a8f93a8f93a8f93a8f93a8f93a8f93"' # Low entropy actually?
    # Let's use a real high entropy string
    # Base64 string of random bytes
    code = 'secret = "mZJ8xR9kL2pQ5sT1vW4yA7nB3cE6fG9h"'
    violations = detect_violations(code)
    # The existing implementation might catch this if it's > 20 chars and entropy > 4.0
    # "mZJ8xR9kL2pQ5sT1vW4yA7nB3cE6fG9h" -> 32 chars.
    # Entropy should be high.

    # Check if we find 'high_entropy_string'
    found = any(v['id'] == 'high_entropy_string' for v in violations)
    assert found

def test_entropy_in_dict_values():
    # Dictionary value - NOT YET SUPPORTED
    code = """
config = {
    "api_key": "mZJ8xR9kL2pQ5sT1vW4yA7nB3cE6fG9h",
    "other": 123
}
    """
    violations = detect_violations(code)
    found = any(v['id'] == 'high_entropy_string' for v in violations)
    assert found

def test_entropy_in_list_values():
    # List value - NOT YET SUPPORTED
    code = 'keys = ["mZJ8xR9kL2pQ5sT1vW4yA7nB3cE6fG9h", "short"]'
    violations = detect_violations(code)
    found = any(v['id'] == 'high_entropy_string' for v in violations)
    assert found

def test_entropy_in_nested_structure():
    # Nested
    code = """
data = {
    "users": [
        {"token": "mZJ8xR9kL2pQ5sT1vW4yA7nB3cE6fG9h"}
    ]
}
    """
    violations = detect_violations(code)
    found = any(v['id'] == 'high_entropy_string' for v in violations)
    assert found

def test_entropy_low_entropy_long_string():
    # Long string but low entropy (e.g. repeated chars)
    code = 'not_secret = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"'
    violations = detect_violations(code)
    found = any(v['id'] == 'high_entropy_string' for v in violations)
    assert not found
