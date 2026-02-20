import os
import pytest
from src.core.scanner.main import Scanner
from src.core.rules import RuleRepository

class TestGoScanning:

    @pytest.fixture
    def setup_rules(self):
        # Ensure rules/go.yaml exists and is loaded
        # The default RuleRepository loads from 'rules/' in project root
        # which should be correct in the test environment
        pass

    def test_scan_go_file(self, setup_rules):
        file_path = "tests/fixtures/go/vulnerable.go"

        # Verify fixture exists
        assert os.path.exists(file_path), "Fixture file missing"

        scanner = Scanner(language='go')
        results = scanner.scan(file_path)

        issues = results['issues']

        # We expect 4 issues:
        # 2x formatted_print
        # 1x empty_block
        # 1x infinite_loop
        # (string_concatenation_in_loop is not in vulnerable.go yet)

        assert len(issues) == 4

        ids = [i['id'] for i in issues]
        assert 'formatted_print' in ids
        assert 'empty_block' in ids
        assert 'infinite_loop' in ids

        # Check specific counts
        assert ids.count('formatted_print') == 2
        assert ids.count('empty_block') == 1
        assert ids.count('infinite_loop') == 1

    def test_scan_go_string_concat(self, tmp_path):
        # Create a temporary Go file with string concatenation
        d = tmp_path / "go_src"
        d.mkdir()
        p = d / "concat.go"
        p.write_text("""
        package main
        func main() {
            s := ""
            for i := 0; i < 10; i++ {
                s += "a"
            }
        }
        """, encoding='utf-8')

        scanner = Scanner(language='go')
        results = scanner.scan(str(p))

        issues = results['issues']
        assert len(issues) == 1
        assert issues[0]['id'] == 'string_concatenation_in_loop'
