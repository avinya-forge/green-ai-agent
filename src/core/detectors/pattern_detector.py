"""
Pattern-based detection strategies for green software violations.
"""

import re
from typing import List, Dict

class PatternBasedDetector:
    """Pattern-based detection using regex for simple violations."""

    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.violations = []

    def detect_all(self) -> List[Dict]:
        """Run all pattern-based detectors."""
        # Pattern detectors moved to AST-based PythonViolationDetector for better reliability
        self._detect_dead_code()
        self._detect_inefficient_data_structures()

        return self.violations

    def _detect_string_concatenation(self) -> None:
        """Detect string concatenation in loops."""
        in_loop = False
        for line_num, line in enumerate(self.lines, 1):
            if re.search(r'\bfor\b', line):
                in_loop = True
            elif re.search(r'^(?!\s)', line):  # Dedent
                in_loop = False

            if in_loop and re.search(r'\+=\s*["\']', line):
                self.violations.append({
                    'id': 'string_concatenation_in_loop',
                    'line': line_num,
                    'severity': 'medium',
                    'message': 'String concatenation in loop creates O(n²) memory allocations.',
                    'pattern_match': 'string_concat_loop'
                })

    def _detect_dead_code(self) -> None:
        """Detect unreachable code."""
        for line_num, line in enumerate(self.lines, 1):
            # Simple pattern: code after return/raise
            if line_num < len(self.lines):
                current = line.strip()
                next_line = self.lines[line_num].strip()

                if current.startswith('return') or current.startswith('raise'):
                    if next_line and not next_line.startswith(('except', 'finally', 'elif', 'else', '@', 'def', 'class')):
                        self.violations.append({
                            'id': 'dead_code_block',
                            'line': line_num + 1,
                            'severity': 'medium',
                            'message': 'Unreachable code after return/raise. Dead code increases memory.',
                            'pattern_match': 'dead_code'
                        })

    def _detect_inefficient_data_structures(self) -> None:
        """Detect inefficient data structure usage."""
        patterns = [
            (r'\.index\([^)]*\)\s*[!=]=', '.index() for lookup (O(n)), use set'),
            (r'\.count\([^)]*\)', '.count() for membership test (O(n)), use set'),
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern, message in patterns:
                if re.search(pattern, line):
                    self.violations.append({
                        'id': 'inefficient_data_structure',
                        'line': line_num,
                        'severity': 'high',
                        'message': message,
                        'pattern_match': 'data_struct_usage'
                    })

    def _detect_pandas_inefficiency(self) -> None:
        """Detect pandas inefficiencies via regex for simple cases."""
        # Already handled by AST visit_Call for iterrows, but regex can catch chained calls etc if needed.
        pass
