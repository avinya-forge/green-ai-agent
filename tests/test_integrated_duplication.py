import os
import tempfile
from src.core.scanner import Scanner


def test_scanner_detects_duplication():
    with tempfile.TemporaryDirectory() as tmpdir:
        code = """


def common_logic():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    return a + b + c + d + e
"""
        with open(os.path.join(tmpdir, "file1.py"), "w") as f:
            f.write(code)
        with open(os.path.join(tmpdir, "file2.py"), "w") as f:
            f.write(code)

        scanner = Scanner(language='python')
        results = scanner.scan(tmpdir)

        issue_ids = [i['id'] for i in results['issues']]
        assert 'code_duplication' in issue_ids

        dupe_issue = next(i for i in results['issues'] if i['id'] == 'code_duplication')
        assert "Duplicate code block found" in dupe_issue['message']


def test_scanner_no_duplication():
    # Verify that unique files dont trigger duplication
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "unique1.py"), "w") as f:
            f.write("def unique_one():\n    return 1\n")
        with open(os.path.join(tmpdir, "unique2.py"), "w") as f:
            f.write("def unique_two():\n    return 2\n")

        scanner = Scanner(language='python')
        results = scanner.scan(tmpdir)

        issue_ids = [i['id'] for i in results['issues']]
        assert 'code_duplication' not in issue_ids
