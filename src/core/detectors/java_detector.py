"""
Java-specific detection strategies for green software violations.
"""

from typing import List, Dict
from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_java
from src.utils.logger import logger

class JavaASTDetector:
    """AST-based detector for Java using Tree-sitter."""

    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.violations = []
        self.tree = None
        self.language = None

        try:
            self.language = Language(tree_sitter_java.language())
            self.parser = Parser(self.language)
            self.tree = self.parser.parse(bytes(self.content, "utf8"))
        except Exception as e:
            logger.error(f"Error initializing Tree-sitter for {file_path}: {e}")

    def detect_all(self) -> List[Dict]:
        """Run all AST-based detectors."""
        if not self.tree:
            return []

        self._detect_excessive_logging()
        self._detect_blocking_io()
        self._detect_string_concatenation()
        self._detect_empty_blocks()

        return self.violations

    def _detect_excessive_logging(self) -> None:
        """Detect System.out.println usage."""
        query_scm = """
        (method_invocation
          object: (field_access
            object: (identifier) @class
            field: (identifier) @field)
          name: (identifier) @method
          (#eq? @class "System")
          (#eq? @field "out")
          (#eq? @method "println"))
        """
        self._run_query(query_scm, 'excessive_logging', 'minor',
                       'System.out.println detected. Use a logger.', 'java_sysout')

    def _detect_blocking_io(self) -> None:
        """Detect blocking I/O like Thread.sleep."""
        # Case 1: Thread.sleep()
        query_simple = """
        (method_invocation
          object: (identifier) @class
          name: (identifier) @method
          (#eq? @class "Thread")
          (#eq? @method "sleep"))
        """
        self._run_query(query_simple, 'blocking_io', 'major',
                       'Thread.sleep() blocks the thread.', 'java_thread_sleep')

        # Case 2: java.lang.Thread.sleep()
        query_fq = """
        (method_invocation
          object: (field_access
            object: (field_access
              object: (identifier) @p1
              field: (identifier) @p2)
            field: (identifier) @class)
          name: (identifier) @method
          (#eq? @p1 "java")
          (#eq? @p2 "lang")
          (#eq? @class "Thread")
          (#eq? @method "sleep"))
        """
        self._run_query(query_fq, 'blocking_io', 'major',
                       'Thread.sleep() blocks the thread.', 'java_thread_sleep')

    def _detect_string_concatenation(self) -> None:
        """Detect string concatenation in loops."""
        # Detect += inside loops
        query_concat = """
        (assignment_expression
          operator: "+="
          right: [(string_literal) (binary_expression)]) @concat
        """

        try:
            query = Query(self.language, query_concat)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            loop_types = ['for_statement', 'while_statement', 'do_statement', 'enhanced_for_statement']

            for _, captures in matches:
                nodes = captures.get('concat', [])
                for node in nodes:
                    # Check if inside loop
                    parent = node.parent
                    in_loop = False
                    while parent:
                        if parent.type in loop_types:
                            in_loop = True
                            break
                        parent = parent.parent

                    if in_loop:
                         self._add_violation(
                            node,
                            'string_concatenation_in_loop',
                            'major',
                            'String concatenation in loop creates unnecessary objects.',
                            'java_string_concat'
                        )
        except Exception as e:
            logger.error(f"Error in string concat detection: {e}")

    def _detect_empty_blocks(self) -> None:
        """Detect empty blocks (catch, if, loops)."""
        query_scm = """
        (block) @block
        """
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
                            'java_empty_block'
                        )
        except Exception as e:
            logger.error(f"Error in empty block detection: {e}")

    def _run_query(self, query_scm: str, rule_id: str, severity: str, message: str, pattern_match: str) -> None:
        """Helper to run tree-sitter queries."""
        try:
            query = Query(self.language, query_scm)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            reported_lines = set()

            for _, captures in matches:
                if not captures:
                    continue

                # Use the first captured node
                first_node = next(iter(captures.values()))[0]
                line = first_node.start_point[0] + 1

                if line not in reported_lines:
                    self.violations.append({
                        'id': rule_id,
                        'line': line,
                        'severity': severity,
                        'message': message,
                        'pattern_match': pattern_match
                    })
                    reported_lines.add(line)
        except Exception as e:
            logger.error(f"Query error ({rule_id}): {e}")

    def _add_violation(self, node, rule_id, severity, message, pattern_match):
        line = node.start_point[0] + 1
        self.violations.append({
            'id': rule_id,
            'line': line,
            'severity': severity,
            'message': message,
            'pattern_match': pattern_match
        })
