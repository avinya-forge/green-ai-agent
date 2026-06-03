import pytest
import os
import tempfile
from src.core.scanner import Scanner

def test_scanner_detects_dead_code():
    with tempfile.TemporaryDirectory() as tmpdir:
        code = """
def used():
    pass

def unused():
    pass

used()
"""
        with open(os.path.join(tmpdir, "code.py"), "w") as f:
            f.write(code)

        scanner = Scanner(language='python')
        results = scanner.scan(tmpdir)

        issue_ids = [i['id'] for i in results['issues']]
        assert 'unused_function' in issue_ids
