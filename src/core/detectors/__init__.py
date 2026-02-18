"""
Detection strategies for green software violations.

This module exports detector classes and the main `detect_violations` function.
"""

from typing import List, Dict

from .python_detector import PythonViolationDetector
from .javascript_detector import JavaScriptASTDetector, JavaScriptViolationDetector
from .pattern_detector import PatternBasedDetector

def detect_violations(content: str, file_path: str, language: str = 'python') -> List[Dict]:
    """
    Detect all violations in code.

    Returns a list of violations with id, line, severity, message, pattern_match.
    """
    violations = []

    if language == 'python':
        # AST-based detection
        ast_detector = PythonViolationDetector(content, file_path)
        violations.extend(ast_detector.detect_all())

        # Pattern-based detection
        pattern_detector = PatternBasedDetector(content, file_path)
        violations.extend(pattern_detector.detect_all())

    elif language == 'javascript':
        # AST-based detection
        js_ast_detector = JavaScriptASTDetector(content, file_path)
        violations.extend(js_ast_detector.detect_all())

        # Regex-based detection (legacy/remaining rules)
        js_detector = JavaScriptViolationDetector(content, file_path)
        violations.extend(js_detector.detect_all())

    return violations
