"""
Unit tests for TypeScriptASTDetector
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.detectors.typescript_detector import TypeScriptASTDetector

class TestTypeScriptVisitors:
    def _get_violations(self, code, file_path="test_file.ts"):
        detector = TypeScriptASTDetector(code, file_path)
        return detector.detect_all()

    def test_any_type_usage(self):
        code = """
        function processData(data: any) {
            console.log(data);
        }
        """
        violations = self._get_violations(code)
        assert any(v['id'] == 'any_type_usage' for v in violations)

    def test_prefer_const_enum(self):
        code = """
        enum Colors {
            Red,
            Green,
            Blue
        }
        """
        violations = self._get_violations(code)
        assert any(v['id'] == 'prefer_const_enum' for v in violations)

    def test_const_enum_no_violation(self):
        code = """
        const enum Colors {
            Red,
            Green,
            Blue
        }
        """
        violations = self._get_violations(code)
        assert not any(v['id'] == 'prefer_const_enum' for v in violations)

    def test_inherited_console_time(self):
        code = """
        console.time('timer');
        // do work
        console.timeEnd('timer');
        """
        violations = self._get_violations(code)
        assert any(v['id'] == 'console_time' for v in violations)

    def test_inherited_empty_block(self):
        code = """
        function doNothing() {
        }
        """
        violations = self._get_violations(code)
        assert any(v['id'] == 'empty_block' for v in violations)

    def test_inherited_magic_numbers(self):
        code = """
        const timeout = 5000;
        """
        violations = self._get_violations(code)
        assert any(v['id'] == 'magic_numbers' for v in violations)

    def test_tsx_file_support(self):
        code = """
        import React from 'react';

        const Component = (props: any) => {
            return <div>{props.name}</div>;
        };
        """
        violations = self._get_violations(code, file_path="component.tsx")
        # Should detect 'any' usage
        assert any(v['id'] == 'any_type_usage' for v in violations)
