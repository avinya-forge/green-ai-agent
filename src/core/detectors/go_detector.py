"""
Go-specific detection strategies for green software violations.
"""

from typing import List, Dict, Set
from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_go
from src.utils.logger import logger
from .base_detector import BaseTreeSitterDetector

# Query Constants
QUERY_FORMATTED_PRINT = """
(call_expression
  function: (selector_expression
    operand: (identifier) @pkg
    field: (field_identifier) @func)
  (#eq? @pkg "fmt")
  (#match? @func "^(Print|Println|Printf)$"))
"""

QUERY_EMPTY_BLOCK = """(block) @block"""

QUERY_INFINITE_LOOP = """(for_statement) @loop"""

QUERY_STRING_CONCAT = """
(assignment_statement
  left: (expression_list (identifier))
  right: (expression_list (interpreted_string_literal))
) @assign_plus_eq

(assignment_statement
  left: (expression_list (identifier))
  right: (expression_list (binary_expression
    operator: "+"
    right: (interpreted_string_literal)
  ))
) @assign_add

(assignment_statement
  left: (expression_list (identifier))
  right: (expression_list (binary_expression
    operator: "+"
  ))
) @assign_any_add
"""

class GoASTDetector(BaseTreeSitterDetector):
    """AST-based detector for Go using Tree-sitter."""

    _CACHED_LANGUAGE = None
    _CACHED_QUERIES = {}

    def __init__(self, content: str, file_path: str):
        if GoASTDetector._CACHED_LANGUAGE is None:
            try:
                GoASTDetector._CACHED_LANGUAGE = Language(tree_sitter_go.language())
            except Exception as e:
                logger.error(f"Failed to initialize Go language: {e}")
                # Fallback handled by Base, though passing None might fail

        # If cache failed, pass module, else pass cached language
        lang_arg = GoASTDetector._CACHED_LANGUAGE if GoASTDetector._CACHED_LANGUAGE else tree_sitter_go
        super().__init__(content, file_path, lang_arg)

    def _get_query(self, query_scm: str) -> Query:
        """Get or compile a query."""
        if not self.language:
            return None

        if query_scm not in GoASTDetector._CACHED_QUERIES:
            try:
                GoASTDetector._CACHED_QUERIES[query_scm] = Query(self.language, query_scm)
            except Exception as e:
                logger.error(f"Failed to compile query for Go: {e}")
                return None
        return GoASTDetector._CACHED_QUERIES.get(query_scm)

    def detect_all(self) -> List[Dict]:
        """Run all AST-based detectors."""
        if not self.tree:
            return []

        self._detect_formatted_print()
        self._detect_empty_blocks()
        self._detect_infinite_loop()
        self._detect_string_concatenation_in_loop()

        return self.violations

    def _detect_formatted_print(self) -> None:
        """Detect fmt.Println/Printf usage (Excessive logging)."""
        query = self._get_query(QUERY_FORMATTED_PRINT)
        if not query:
            return

        cursor = QueryCursor(query)
        matches = cursor.matches(self.tree.root_node)

        rule_id = 'formatted_print'
        severity = 'minor'
        message = 'fmt.Print* detected. Use a logger or remove in production.'
        pattern_match = 'go_fmt_print'

        reported_lines = set()

        for _, captures in matches:
            if not captures:
                continue
            first_node = next(iter(captures.values()))[0]
            line = first_node.start_point[0] + 1

            if line not in reported_lines:
                self._add_violation_struct(rule_id, line, severity, message, pattern_match)
                reported_lines.add(line)

    def _detect_empty_blocks(self) -> None:
        """Detect empty blocks."""
        query = self._get_query(QUERY_EMPTY_BLOCK)
        if not query:
            return

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

    def _detect_infinite_loop(self) -> None:
        """Detect infinite loops (for {})."""
        query = self._get_query(QUERY_INFINITE_LOOP)
        if not query:
            return

        cursor = QueryCursor(query)
        matches = cursor.matches(self.tree.root_node)

        for _, captures in matches:
            nodes = captures.get('loop', [])
            for node in nodes:
                if node.named_child_count == 1 and node.named_children[0].type == 'block':
                    self._add_violation(
                        node,
                        'infinite_loop',
                        'critical',
                        'Infinite loop detected (for {}). Ensure break condition exists.',
                        'go_infinite_loop'
                    )

    def _detect_string_concatenation_in_loop(self) -> None:
        """Detect string concatenation inside loops (O(n^2))."""
        query = self._get_query(QUERY_STRING_CONCAT)
        if not query:
            return

        cursor = QueryCursor(query)
        matches = cursor.matches(self.tree.root_node)

        str_indicators = {'str', 'name', 'text', 'msg', 'message', 'sql', 'html', 'json', 'xml', 'query', 'url', 'path'}
        processed_nodes: Set[int] = set()

        for _, captures in matches:
            # 1. Check assign_plus_eq (s += "literal")
            nodes = captures.get('assign_plus_eq', [])
            for node in nodes:
                if node.id in processed_nodes:
                    continue

                # Check for += operator
                has_plus_eq = False
                for child in node.children:
                    if child.type == '+=':
                        has_plus_eq = True
                        break

                if has_plus_eq and self._is_in_loop(node):
                     self._add_violation(
                        node,
                        'string_concatenation_in_loop',
                        'high',
                        'String concatenation in loop detected. Use strings.Builder for efficiency.',
                        'go_str_concat'
                    )
                     processed_nodes.add(node.id)

            # 2. Check assign_add (s = s + "literal")
            nodes = captures.get('assign_add', [])
            for node in nodes:
                if node.id in processed_nodes:
                    continue

                if self._is_in_loop(node):
                     self._add_violation(
                        node,
                        'string_concatenation_in_loop',
                        'high',
                        'String concatenation in loop detected. Use strings.Builder for efficiency.',
                        'go_str_concat'
                    )
                     processed_nodes.add(node.id)

            # 3. Check assign_any_add (heuristic: s = s + var)
            nodes = captures.get('assign_any_add', [])
            for node in nodes:
                if node.id in processed_nodes:
                    continue

                # Heuristic: Check if variable name suggests a string
                is_string_var = False

                # Try to get left side identifier
                left_nodes = node.children_by_field_name('left')
                if not left_nodes: continue

                # Assuming expression_list -> identifier
                expr_list = left_nodes[0]
                if expr_list.child_count > 0:
                    identifier = expr_list.child(0)
                    if identifier.type == 'identifier':
                        var_name = identifier.text.decode('utf-8').lower()
                        is_string_var = any(s in var_name for s in str_indicators)

                if is_string_var and self._is_in_loop(node):
                     self._add_violation(
                        node,
                        'string_concatenation_in_loop',
                        'high',
                        'String concatenation in loop detected (heuristic). Use strings.Builder for efficiency.',
                        'go_str_concat'
                    )
                     processed_nodes.add(node.id)

    def _is_in_loop(self, node) -> bool:
        """Check if node is inside a loop (for statement)."""
        parent = node.parent
        while parent:
            if parent.type == 'for_statement':
                return True
            parent = parent.parent
        return False
