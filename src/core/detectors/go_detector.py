"""
Go-specific detection strategies for green software violations.
"""

from typing import List, Dict
from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_go
from src.utils.logger import logger
from .base_detector import BaseTreeSitterDetector

class GoASTDetector(BaseTreeSitterDetector):
    """AST-based detector for Go using Tree-sitter."""

    def __init__(self, content: str, file_path: str):
        super().__init__(content, file_path, tree_sitter_go)

    def detect_all(self) -> List[Dict]:
        """Run all AST-based detectors."""
        if not self.tree:
            return []

        self._detect_formatted_print()
        self._detect_empty_blocks()
        self._detect_infinite_loop()

        return self.violations

    def _detect_formatted_print(self) -> None:
        """Detect fmt.Println/Printf usage (Excessive logging)."""
        query_scm = """
        (call_expression
          function: (selector_expression
            operand: (identifier) @pkg
            field: (field_identifier) @func)
          (#eq? @pkg "fmt")
          (#match? @func "^(Print|Println|Printf)$"))
        """
        self._run_query(query_scm, 'formatted_print', 'minor',
                       'fmt.Print* detected. Use a logger or remove in production.', 'go_fmt_print')

    def _detect_empty_blocks(self) -> None:
        """Detect empty blocks."""
        self._detect_empty_blocks_generic("(block) @block")

    def _detect_infinite_loop(self) -> None:
        """Detect infinite loops (for {})."""
        # In Go, a for loop without clauses is infinite.
        query_scm = """
        (for_statement) @loop
        """

        try:
            query = Query(self.language, query_scm)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            for _, captures in matches:
                nodes = captures.get('loop', [])
                for node in nodes:
                    # Check named_child_count.
                    # for {} -> named_child_count == 1 (the block)
                    if node.named_child_count == 1 and node.named_children[0].type == 'block':
                        self._add_violation(
                            node,
                            'infinite_loop',
                            'critical',
                            'Infinite loop detected (for {}). Ensure break condition exists.',
                            'go_infinite_loop'
                        )
        except Exception as e:
            logger.error(f"Error in infinite loop detection: {e}")
