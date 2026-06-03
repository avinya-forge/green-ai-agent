"""
Pattern-based detection strategies for green software violations.
"""

import re
from typing import List, Dict


class PatternBasedDetector:
    """Pattern-based detection using regex for simple violations."""

    def __init__(self, content: str, file_path: str, rules: List[Dict] = None):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.violations = []
        self.rules = rules or []

    def detect_all(self) -> List[Dict]:
        """Run all pattern-based detectors."""
        self._detect_from_yaml_rules()
        self._detect_dead_code()
        self._detect_inefficient_data_structures()

        return self.violations

    def _detect_from_yaml_rules(self) -> None:
        """Apply regex patterns defined in YAML rules."""
        for rule in self.rules:
            pattern_str = rule.get('pattern')
            if not pattern_str or not pattern_str.strip():
                continue

            try:
                # Strip leading/trailing whitespace from pattern to avoid newline issues from YAML |
                clean_pattern = pattern_str.strip()
                regex = re.compile(clean_pattern, re.IGNORECASE)

                for line_num, line in enumerate(self.lines, 1):
                    if regex.search(line.strip()):
                        self.violations.append({
                            'id': rule['id'],
                            'line': line_num,
                            'severity': rule.get('severity', 'medium'),
                            'message': rule.get('description', rule.get('message', 'N/A')),
                            'pattern_match': 'yaml_regex'
                        })
            except Exception:
                continue

    def _detect_dead_code(self) -> None:
        """Detect unreachable code."""
        for line_num, line in enumerate(self.lines, 1):
            if line_num < len(self.lines):
                current = line.strip()
                next_line = self.lines[line_num].strip()
                if current.startswith('return') or current.startswith('raise'):
                    if next_line and not next_line.startswith(('except', 'finally', 'elif', 'else', '@', 'def', 'class')):
                        self.violations.append({
                            'id': 'dead_code_block',
                            'line': line_num + 1,
                            'severity': 'medium',
                            'message': 'Unreachable code after return/raise.',
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
