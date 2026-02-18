import pytest
from src.core.detectors import detect_violations

def test_sql_injection_f_string():
    code = """
def get_user(cursor, username):
    cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")
"""
    violations = detect_violations(code, "test.py", "python")

    found = any(v['id'] == 'sql_injection_risk' for v in violations)
    assert found
    assert any(v['message'].startswith('Possible SQL injection') for v in violations)

def test_sql_injection_percent_formatting():
    code = """
def get_user(cursor, user_id):
    query = "SELECT * FROM users WHERE id = %s" % user_id
    cursor.execute(query)
"""
    # Note: Our simple detector checks arg to execute(), so if query is a variable, it might miss it unless we track variables.
    # The detector currently checks: execute("..." % ...) or execute(f"...") or execute("...".format(...))
    # If the user passes a variable, we don't catch it yet (simplification).

    # Let's test the direct usage case:
    code_direct = """
def get_user(cursor, user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)
"""
    violations = detect_violations(code_direct, "test.py", "python")
    found = any(v['id'] == 'sql_injection_risk' for v in violations)
    assert found

def test_requests_timeout_missing():
    code = """
import requests

def fetch():
    requests.get("https://example.com")
"""
    violations = detect_violations(code, "test.py", "python")

    found = any(v['id'] == 'requests_without_timeout' for v in violations)
    assert found

def test_requests_timeout_present():
    code = """
import requests

def fetch():
    requests.get("https://example.com", timeout=10)
"""
    violations = detect_violations(code, "test.py", "python")

    found = any(v['id'] == 'requests_without_timeout' for v in violations)
    assert not found

def test_requests_generic_call_timeout():
    code = """
import requests

def fetch():
    requests.request("GET", "https://example.com", timeout=5)
"""
    violations = detect_violations(code, "test.py", "python")
    found = any(v['id'] == 'requests_without_timeout' for v in violations)
    assert not found
