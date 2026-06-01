import os
import json
from pathlib import Path
from src.core.scanner.main import Scanner
from src.core.scanner.baseline_helper import get_violation_fingerprint, load_baseline, filter_with_baseline

def test_baseline_creation_and_filtering(tmp_path):
    # Setup test file with violations
    test_file = tmp_path / "test.py"
    test_file.write_text("import logging\nlogging.info('test')\nlogging.info('test2')")

    # Change working directory to tmp_path for .green-ai directory
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # 1. Create baseline
        scanner = Scanner(language='python')
        results = scanner.scan(str(test_file))
        assert len(results['issues']) >= 2

        baseline_dir = Path('.green-ai')
        baseline_dir.mkdir(exist_ok=True)
        baseline_file = baseline_dir / 'baseline.json'

        baseline_data = {
            'violations': [
                {
                    'id': issue['id'],
                    'file': issue['file'],
                    'line': issue['line'],
                    'fingerprint': get_violation_fingerprint(issue)
                } for issue in results['issues']
            ]
        }
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f)

        # 2. Verify filtering
        baseline = load_baseline()
        assert baseline is not None

        new_issues, skipped, fixed = filter_with_baseline(results['issues'], baseline)
        assert skipped == len(results['issues'])
        assert len(new_issues) == 0

        # 3. Add a new violation
        test_file.write_text("import logging\nlogging.info('test')\nlogging.info('test2')\nlogging.info('new')")
        results2 = scanner.scan(str(test_file))

        new_issues2, skipped2, fixed2 = filter_with_baseline(results2['issues'], baseline)
        assert len(new_issues2) >= 1

    finally:
        os.chdir(old_cwd)

def test_inline_suppression():
    from src.core.scanner.suppression import get_suppressions, is_suppressed

    content = """
# green-ai: ignore next-line excessive_logging reason="Testing"
print("test")
"""
    suppressions = get_suppressions(content)
    assert 3 in suppressions
    assert "excessive_logging" in suppressions[3]

    issue = {'id': 'excessive_logging', 'line': 3, 'file': 'test.py'}
    assert is_suppressed(issue, suppressions)

    issue2 = {'id': 'other_rule', 'line': 3, 'file': 'test.py'}
    assert not is_suppressed(issue2, suppressions)

def test_external_suppression(tmp_path):
    from src.core.scanner.suppression import is_suppressed

    external = [
        {'rule_id': 'test_rule', 'file': 'test.py', 'reason': 'Test'}
    ]

    issue = {'id': 'test_rule', 'line': 10, 'file': 'test.py'}
    assert is_suppressed(issue, {}, external)

    issue2 = {'id': 'test_rule', 'line': 10, 'file': 'other.py'}
    assert not is_suppressed(issue2, {}, external)
