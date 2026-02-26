import os
import shutil
import pytest
from click.testing import CliRunner
from src.cli.main import cli
from src.core.scanner.worker import scan_file_worker
from src.core.detectors import detect_violations
from src.utils.entropy import calculate_shannon_entropy
from src.core.detectors.cache import detection_cache

def test_init_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['init'])
        assert result.exit_code == 0, f"Init failed: {result.output}"
        assert os.path.exists('.green-ai.yaml')
        with open('.green-ai.yaml', 'r') as f:
            content = f.read()
            assert "# Green-AI Configuration File" in content

def test_entropy_utility():
    assert calculate_shannon_entropy("aaaaa") == 0.0
    assert calculate_shannon_entropy("abcde") > 2.0

def test_python_entropy_detection():
    # Needs to be > 20 chars and > 4.0 entropy
    content = 'key = "sk-proj-1234567890abcdef1234567890abcdef1234567890abcdef"'
    # We pass file_path="test.py" so it picks python detector
    violations = detect_violations(content, "test.py", "python")

    found = False
    for v in violations:
        if v['id'] == 'high_entropy_string':
            found = True
            break

    assert found, f"Violations found: {violations}"

def test_js_entropy_detection():
    # Needs to be > 20 chars and > 4.0 entropy
    content = 'const key = "sk-proj-1234567890abcdef1234567890abcdef1234567890abcdef";'
    # We pass file_path="test.js" so it picks js detector
    violations = detect_violations(content, "test.js", "javascript")

    found = False
    for v in violations:
        if v['id'] == 'high_entropy_string':
            found = True
            break

    assert found, f"Violations found: {violations}"

def test_severity_override():
    # Create dummy file in current dir (pytest temp dir usually)
    with open('test_override.py', 'w') as f:
        f.write("def foo():\n    pass\n")

    try:
        config = {
            'rules': {
                'severity': {
                    'empty_block': 'critical'
                },
                'enabled': ['empty_block']
            }
        }
        rules = [{'id': 'empty_block', 'severity': 'minor'}]

        result = scan_file_worker('test_override.py', 'python', config, rules)
        issues = result['issues']
        target_issue = next((i for i in issues if i['id'] == 'empty_block'), None)

        assert target_issue is not None
        assert target_issue['severity'] == 'critical'
    finally:
        if os.path.exists('test_override.py'):
            os.remove('test_override.py')

def test_caching():
    detection_cache.cache.clear()
    content = "x = 1"
    detect_violations(content, "test.py", "python")
    assert len(detection_cache.cache) == 1
    detect_violations(content, "test.py", "python")
    assert len(detection_cache.cache) == 1
