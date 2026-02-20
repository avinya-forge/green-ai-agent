"""
Java-specific detection strategies for green software violations.
"""

from typing import List, Dict
from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_java
from src.utils.logger import logger
from .base_detector import BaseTreeSitterDetector

class JavaASTDetector(BaseTreeSitterDetector):
    """AST-based detector for Java using Tree-sitter."""

    def __init__(self, content: str, file_path: str):
        super().__init__(content, file_path, tree_sitter_java)

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
        self._detect_empty_blocks_generic("(block) @block")
