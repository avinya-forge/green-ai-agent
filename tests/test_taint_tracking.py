import pytest
from src.core.detectors.python_detector import PythonViolationDetector

def test_sql_injection_taint():
    code = """
def search_users(request):
    username = request.GET.get('username')
    cursor.execute("SELECT * FROM users WHERE username = " + username)
"""
    detector = PythonViolationDetector(code, "test.py")
    violations = detector.detect_all()

    taint_violations = [v for v in violations if v['id'] == 'sql_injection_taint']
    assert len(taint_violations) == 1
    assert "Tainted variable" in taint_violations[0]['message']

def test_command_injection_taint():
    code = """
import sys
import subprocess

def run_cmd():
    user_input = sys.argv[1]
    subprocess.run(f"ls -l {user_input}", shell=True)
"""
    detector = PythonViolationDetector(code, "test.py")
    violations = detector.detect_all()

    taint_violations = [v for v in violations if v['id'] == 'command_injection_taint']
    assert len(taint_violations) == 1
    assert "Tainted variable" in taint_violations[0]['message']

def test_ssrf_taint():
    code = """
import requests
import os

def fetch_url():
    target_url = os.environ.get('TARGET_URL')
    requests.get(target_url)
"""
    detector = PythonViolationDetector(code, "test.py")
    violations = detector.detect_all()

    taint_violations = [v for v in violations if v['id'] == 'ssrf_injection_taint']
    assert len(taint_violations) == 1
    assert "Tainted variable" in taint_violations[0]['message']
