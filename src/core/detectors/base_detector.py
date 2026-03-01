"""
Base classes for detectors.
"""

from typing import List, Dict, Optional, Any
from tree_sitter import Language, Parser, Query, QueryCursor
from src.utils.logger import logger

class BaseTreeSitterDetector:
    """
    Base class for AST-based detectors using Tree-sitter.

    Provides common functionality for initialization, query execution,
    and violation reporting.
    """

    def __init__(self, content: str, file_path: str, language_lib: Any):
        """
        Initialize the detector.

        Args:
            content: The source code content.
            file_path: The path to the file.
            language_lib: The tree-sitter language library (e.g., tree_sitter_java).
        """
        self.content = content
        self.file_path = file_path
        self.violations: List[Dict] = []
        self.tree = None
        self.language = None
        self.language_lib = language_lib

        try:
            # Handle special cases where language_lib might need specific init (like TS)
            # But mostly it's language_lib.language()
            if isinstance(language_lib, Language):
                 self.language = language_lib
            elif hasattr(language_lib, 'language'):
                 self.language = Language(language_lib.language())
            else:
                 # Fallback or direct object
                 self.language = Language(language_lib)

            self.parser = Parser(self.language)
            self.tree = self.parser.parse(bytes(self.content, "utf8"))
        except Exception as e:
            logger.error(f"Error initializing Tree-sitter for {file_path}: {e}")

    def dispose(self):
        """
        Dispose of the tree and parser to free memory.
        """
        self.tree = None
        self.parser = None
        self.language = None

    def detect_all(self) -> List[Dict]:
        """
        Run all AST-based detectors.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def _run_query(self, query_scm: str, rule_id: str, severity: str, message: str, pattern_match: str) -> None:
        """
        Helper to run tree-sitter queries and add violations.

        Args:
            query_scm: The S-expression query string.
            rule_id: The ID of the rule.
            severity: The severity level (minor, major, critical).
            message: The user-facing message.
            pattern_match: A unique identifier for the pattern match.
        """
        if not self.tree:
            return

        try:
            query = Query(self.language, query_scm)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            reported_lines = set()

            for _, captures in matches:
                if not captures:
                    continue

                # Use the first captured node
                # captures is a dict {name: [node, ...]} in newer bindings
                first_node = next(iter(captures.values()))[0]
                line = first_node.start_point[0] + 1

                if line not in reported_lines:
                    self._add_violation_struct(rule_id, line, severity, message, pattern_match)
                    reported_lines.add(line)
        except Exception as e:
            logger.error(f"Query error ({rule_id}) in {self.file_path}: {e}")

    def _add_violation(self, node, rule_id, severity, message, pattern_match):
        """Add violation from a node."""
        line = node.start_point[0] + 1
        self._add_violation_struct(rule_id, line, severity, message, pattern_match)

    def _add_violation_struct(self, rule_id, line, severity, message, pattern_match):
        """Add violation structure directly."""
        self.violations.append({
            'id': rule_id,
            'line': line,
            'severity': severity,
            'message': message,
            'pattern_match': pattern_match
        })

    def _detect_empty_blocks_generic(self, query_scm: str) -> None:
        """
        Generic empty block detection.

        Args:
            query_scm: The S-expression query to find blocks (must capture @block).
        """
        if not self.tree:
            return

        try:
            query = Query(self.language, query_scm)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            for _, captures in matches:
                nodes = captures.get('block', [])
                for node in nodes:
                    if node.named_child_count == 0:
                         self._add_violation(
                            node,
                            'empty_block',
                            'minor',
                            'Empty block detected.',
                            'empty_block'
                        )
        except Exception as e:
            logger.error(f"Error in empty block detection: {e}")
