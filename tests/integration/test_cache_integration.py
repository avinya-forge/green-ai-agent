import os
import time
import json
import pytest
from src.core.scanner import Scanner
import shutil

@pytest.fixture
def clean_cache():
    cache_dir = os.path.expanduser(".green-ai/cache")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    yield
    # Cleanup after test
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

def test_disk_cache_integration(tmp_path, clean_cache):
    """Verify that disk cache is created and used during scans."""
    # 1. Create a Python file with a known violation (infinite loop)
    test_file = tmp_path / "test_loop.py"
    # Create directory if needed (tmp_path is a directory)

    code = "while True:\n    pass\n"
    test_file.write_text(code, encoding="utf-8")

    # 2. Run scan
    # Create a temporary config to enable caching and no_infinite_loops
    config_file = tmp_path / ".green-ai.yaml"
    config_file.write_text("""
rules:
  enabled: []
  disabled: [] # Ensure nothing is disabled
cache:
  enabled: true
  path: .green-ai/cache
""", encoding="utf-8")

    scanner = Scanner(language="python", config_path=str(config_file))
    result1 = scanner.scan(str(test_file))

    # Verify we found the issue
    issues = result1['issues']
    if len(issues) == 0:
        print(f"Scan Result: {result1}")
    assert len(issues) > 0
    assert any(i['id'] == 'no_infinite_loops' for i in issues)

    # 3. Check if cache files exist
    cache_dir = os.path.expanduser(".green-ai/cache")
    assert os.path.exists(cache_dir)

    json_files = []
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))

    assert len(json_files) > 0, "No cache files created in .green-ai/cache"

    # 4. Verify content of cache file
    with open(json_files[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert 'violations' in data
        # The cache stores raw violations, not full issues
        violations = data['violations']
        assert len(violations) > 0
        ids = [v['id'] for v in violations]
        assert 'no_infinite_loops' in ids

    # 5. Run scan again and ensure results are consistent
    result2 = scanner.scan(str(test_file))
    # Note: result2['issues'] are filtered by rules, so it might differ from raw cache violations
    # But result1['issues'] should match result2['issues']

    assert len(result2['issues']) == len(result1['issues'])
    if len(result2['issues']) > 0:
        assert result2['issues'][0]['id'] == result1['issues'][0]['id']

def test_cache_invalidation_on_change(tmp_path, clean_cache):
    """Verify cache is invalidated/bypassed when file content changes."""
    test_file = tmp_path / "test_change.py"

    # Config file
    config_file = tmp_path / ".green-ai.yaml"
    config_file.write_text("""
rules:
  enabled: []
  disabled: []
cache:
  enabled: true
  path: .green-ai/cache
""", encoding="utf-8")

    # Initial content
    test_file.write_text("while True:\n    pass\n", encoding="utf-8")
    scanner = Scanner(language="python", config_path=str(config_file))
    scanner.scan(str(test_file))

    # Change content (remove violation)
    test_file.write_text("x = 1\n", encoding="utf-8")

    result = scanner.scan(str(test_file))
    assert len(result['issues']) == 0
