"""
JavaScript-specific detection strategies for green software violations.
"""

import re
from typing import List, Dict
from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_javascript
from src.utils.logger import logger
from .base_detector import BaseTreeSitterDetector

class JavaScriptASTDetector(BaseTreeSitterDetector):
    """AST-based detector for JavaScript using Tree-sitter."""

    def __init__(self, content: str, file_path: str, language_lib=tree_sitter_javascript):
        super().__init__(content, file_path, language_lib)

    def detect_all(self) -> List[Dict]:
        """Run all AST-based detectors."""
        if not self.tree:
            return []

        self._detect_excessive_logging()
        self._detect_console_time()
        self._detect_eval()
        self._detect_magic_numbers()
        self._detect_deprecated_apis()
        self._detect_inefficient_browser_apis()
        self._detect_sync_io()
        self._detect_loops()
        self._detect_dom_manipulation()
        self._detect_inner_html()
        self._detect_string_concatenation()
        self._detect_empty_blocks()

        return self.violations

    def _detect_empty_blocks(self) -> None:
        """Detect empty blocks."""
        self._detect_empty_blocks_generic("(statement_block) @block")

    def _detect_console_time(self) -> None:
        """Detect console.time usage."""
        query_scm = """
        (call_expression
          function: (member_expression
            object: (identifier) @obj
            property: (property_identifier) @prop)
          (#eq? @obj "console")
          (#match? @prop "^(time|timeEnd)$"))
        """
        self._run_query(query_scm, 'console_time', 'minor',
                       'console.time/timeEnd detected. Remove in production.', 'console_time')

    def _detect_inner_html(self) -> None:
        """Detect innerHTML usage."""
        query_scm = """
        (assignment_expression
          left: (member_expression
            property: (property_identifier) @prop)
          (#eq? @prop "innerHTML"))
        """
        self._run_query(query_scm, 'inner_html', 'major',
                       'Avoid innerHTML. Use textContent or DOM methods.', 'inner_html')

    def _detect_excessive_logging(self) -> None:
        """Detect console.log usage."""
        query_scm = """
        (call_expression
          function: (member_expression
            object: (identifier) @obj
            property: (property_identifier) @prop)
          (#eq? @obj "console")
          (#match? @prop "^(log|debug|info)$"))
        """
        self._run_query(query_scm, 'excessive_console_logging', 'minor',
                       'Console logging detected. Remove in production.', 'console_log')

    def _detect_eval(self) -> None:
        """Detect eval usage."""
        query_scm = """
        (call_expression
          function: (identifier) @func
          (#eq? @func "eval"))
        """
        self._run_query(query_scm, 'eval_usage', 'critical',
                       'Eval is a security risk and slow.', 'eval_usage')

    def _detect_magic_numbers(self) -> None:
        """Detect magic numbers."""
        query_scm = """
        (number) @num
        """
        try:
            query = Query(self.language, query_scm)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            for _, captures in matches:
                nodes = captures.get('num', [])
                for node in nodes:
                    # Tree-sitter returns bytes, decode to string
                    text = node.text.decode('utf8')
                    try:
                        # Handle floats and ints
                        val = float(text)
                        if val >= 100 and val not in [1000, 1024, 3600]:
                             self.violations.append({
                                'id': 'magic_numbers',
                                'line': node.start_point[0] + 1,
                                'severity': 'minor',
                                'message': f'Magic number "{val}" usage. Use named constants.',
                                'pattern_match': 'magic_number_js'
                            })
                    except ValueError:
                        pass
        except Exception as e:
            logger.error(f"Query error (magic_numbers): {e}")

    def _detect_deprecated_apis(self) -> None:
        """Detect deprecated or heavy libraries/APIs."""
        # 1. document.write
        query_doc_write = """
        (call_expression
          function: (member_expression
            object: (identifier) @obj
            property: (property_identifier) @prop)
          (#eq? @obj "document")
          (#eq? @prop "write"))
        """
        self._run_query(query_doc_write, 'document_write', 'critical',
                        'document.write blocks rendering.', 'document_write')

        # 2. moment.js (require or import)
        # require('moment')
        query_require_moment = """
        (call_expression
          function: (identifier) @func
          arguments: (arguments (string (string_fragment) @arg))
          (#eq? @func "require")
          (#match? @arg "moment"))
        """
        self._run_query(query_require_moment, 'momentjs_deprecated', 'major',
                        'Moment.js is heavy. Use Day.js or Date.', 'momentjs_deprecated')

        # import ... from 'moment'
        query_import_moment = """
        (import_statement
            source: (string (string_fragment) @source)
            (#match? @source "moment"))
        """
        self._run_query(query_import_moment, 'momentjs_deprecated', 'major',
                        'Moment.js is heavy. Use Day.js or Date.', 'momentjs_deprecated')

    def _detect_inefficient_browser_apis(self) -> None:
        """Detect inefficient browser APIs."""
        # setInterval
        query_set_interval = """
        (call_expression
          function: (identifier) @func
          (#eq? @func "setInterval"))
        """
        self._run_query(query_set_interval, 'setInterval_animation', 'major',
                        'Use requestAnimationFrame instead of setInterval.', 'setInterval_animation')

        # window.alert/prompt/confirm
        # Can be called as alert() or window.alert()
        # Case 1: alert()
        query_alert_global = """
        (call_expression
          function: (identifier) @func
          (#match? @func "^(alert|prompt|confirm)$"))
        """
        self._run_query(query_alert_global, 'alert_usage', 'minor',
                        'Native dialogs block the main thread.', 'alert_usage')

        # Case 2: window.alert()
        query_alert_window = """
        (call_expression
          function: (member_expression
            object: (identifier) @obj
            property: (property_identifier) @prop)
          (#eq? @obj "window")
          (#match? @prop "^(alert|prompt|confirm)$"))
        """
        self._run_query(query_alert_window, 'alert_usage', 'minor',
                        'Native dialogs block the main thread.', 'alert_usage')

    def _detect_sync_io(self) -> None:
        """Detect synchronous I/O."""
        # readFileSync
        query_read_file_sync = """
        (call_expression
          function: (member_expression
            property: (property_identifier) @prop)
          (#match? @prop "readFileSync"))
        """
        self._run_query(query_read_file_sync, 'synchronous_io', 'major',
                        'Synchronous I/O blocks the main thread. Use async APIs.', 'sync_io_js')

        # XMLHttpRequest
        query_xhr = """
        (new_expression
            constructor: (identifier) @cons
            (#eq? @cons "XMLHttpRequest"))
        """
        self._run_query(query_xhr, 'synchronous_io', 'major',
                        'Synchronous I/O blocks the main thread. Use fetch().', 'sync_io_js')

    def _detect_loops(self) -> None:
        """Detect loop related violations (infinite, nested, inefficient)."""
        # 1. Infinite loops: while(true)
        query_infinite = """
        (while_statement
          condition: (parenthesized_expression (true))) @infinite
        """
        self._run_query(query_infinite, 'no_infinite_loops', 'critical',
                        'Infinite loop detected (while(true)).', 'infinite_while_js')

        # 2. Inefficient C-style loops
        query_c_loop = """
        (for_statement) @loop
        """
        self._run_query(query_c_loop, 'inefficient_loop', 'major',
                        'C-style for loop detected. Consider using .map(), .filter(), or .reduce() for better optimization.', 'c_style_for')

        # 3. Nested loops (Depth check)
        # We need to traverse the tree or query for loops inside loops
        # Simple query for direct nesting:
        query_nested = """
        (for_statement body: (statement_block (for_statement))) @nested
        """
        # Note: This only catches depth 2. For deeper nesting we might need a more general traversal or multiple queries.
        # But let's start with depth 2 which is the main concern.

        # Actually, let's try to be more generic.
        # Find all loops, then check their ancestors.
        loop_types = ['for_statement', 'while_statement', 'do_statement', 'for_in_statement']
        # Helper to check depth

        try:
             # Find all loops
             query_loops = "[(for_statement) (while_statement) (do_statement) (for_in_statement)] @loop"
             query = Query(self.language, query_loops)
             cursor = QueryCursor(query)
             matches = cursor.matches(self.tree.root_node)

             # Include for_of_statement
             extended_loop_types = loop_types

             for _, captures in matches:
                 for _, nodes in captures.items():
                     for node in nodes:
                         depth = 0
                         parent = node.parent
                         while parent:
                             if parent.type in extended_loop_types:
                                 depth += 1
                             parent = parent.parent

                         if depth >= 1: # 1 parent loop means depth 2
                             total_depth = depth + 1
                             severity = 'critical' if total_depth >= 3 else 'major'
                             # We need to manually add violation because _run_query deduplicates by line and doesn't support dynamic message
                             line = node.start_point[0] + 1
                             # Check if we already reported this line (maybe not needed as we iterate nodes)

                             self.violations.append({
                                'id': 'no_n2_algorithms',
                                'line': line,
                                'severity': severity,
                                'message': f'Nesting depth {total_depth}: Potential O(n^{total_depth}) complexity detected.',
                                'pattern_match': 'nested_loop_js'
                            })
        except Exception as e:
            logger.error(f"Error in nested loop detection: {e}")

    def _detect_dom_manipulation(self) -> None:
        """Detect DOM manipulation."""
        # Direct DOM query
        query_dom = """
        (call_expression
           function: (member_expression
             object: (identifier) @obj
             property: (property_identifier) @prop)
           (#eq? @obj "document")
           (#match? @prop "^(querySelector|getElementById)$"))
        """
        self._run_query(query_dom, 'unnecessary_dom_manipulation', 'major',
                        'Direct DOM query/manipulation. Cache references.', 'dom_query')

        # DOM in loop
        # Find DOM methods inside loops
        dom_methods = ["appendChild", "innerHTML", "textContent", "setAttribute", "classList", "write"]
        dom_methods_regex = "^(" + "|".join(dom_methods) + ")$"

        query_dom_loop = f"""
        (call_expression
           function: (member_expression
             property: (property_identifier) @prop)
           (#match? @prop "{dom_methods_regex}"))

        (assignment_expression
           left: (member_expression
             property: (property_identifier) @prop)
           (#match? @prop "{dom_methods_regex}"))
        """

        try:
            query = Query(self.language, query_dom_loop)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            loop_types = ['for_statement', 'while_statement', 'do_statement', 'for_in_statement', 'for_of_statement']

            for _, captures in matches:
                # We only care about the @prop capture
                nodes = captures.get('prop', [])
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
                         # Extract method name for message
                         method_name = node.text.decode('utf8')

                         self.violations.append({
                            'id': 'unnecessary_dom_manipulation',
                            'line': node.start_point[0] + 1,
                            'severity': 'critical',
                            'message': f'DOM manipulation "{method_name}" inside loop. Causes reflows/repaints. Batch updates.',
                            'pattern_match': 'dom_in_loop'
                        })
        except Exception as e:
            logger.error(f"Error in DOM loop detection: {e}")

    def _detect_string_concatenation(self) -> None:
        """Detect string concatenation in loops."""
        # += with string
        # We can't easily check type, but we can check if it looks like a string literal or we can be conservative.
        # The regex version just checked for += and quote.
        # Let's check for += and string literal on RHS.

        query_concat = """
        (augmented_assignment_expression
          operator: ("+=")
          right: [(string) (template_string)]) @concat
        """

        try:
            query = Query(self.language, query_concat)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            loop_types = ['for_statement', 'while_statement', 'do_statement', 'for_in_statement', 'for_of_statement']

            for _, captures in matches:
                for _, nodes in captures.items():
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
                             self.violations.append({
                                'id': 'string_concatenation',
                                'line': node.start_point[0] + 1,
                                'severity': 'major',
                                'message': 'String concatenation in loop creates new objects repeatedly.',
                                'pattern_match': 'string_concat_js'
                            })
        except Exception as e:
            logger.error(f"Error in string concat detection: {e}")


class JavaScriptViolationDetector:
    """Pattern-based detector for JavaScript violations."""

    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.violations = []

    def detect_all(self) -> List[Dict]:
        """Run all JavaScript detectors."""
        self._detect_unused_variables(file_path=self.file_path)
        # Other rules migrated to AST-based detector

        return self.violations

    def _detect_unused_variables(self, file_path=None) -> None:
        """Detect unused variables (basic heuristic)."""
        # Find declarations: let/const/var name = ...
        # Dictionary to track counts
        var_counts = {}
        declarations = []

        # 1. Find all words to count usage (simple tokenizer)
        words = re.findall(r'\b\w+\b', self.content)
        for word in words:
            var_counts[word] = var_counts.get(word, 0) + 1

        # 2. Find specific declarations to report errors
        pattern = r'(let|const|var)\s+(\w+)\s*='
        for line_num, line in enumerate(self.lines, 1):
            matches = re.finditer(pattern, line)
            for match in matches:
                var_name = match.group(2)
                # Filter out likely false positives (short vars, exports, etc if needed)
                if len(var_name) > 1:
                    declarations.append((var_name, line_num))

        # 3. Check if declared vars are used elsewhere
        for var_name, line_num in declarations:
            # If count is 1, it matches only the detected declaration (roughly)
            # This is a heuristic and can be fooled by comments / strings,
            # but fits the "basic regex check" requirement.
            if var_counts.get(var_name, 0) == 1:
                self.violations.append({
                    'id': 'unused_variables',
                    'line': line_num,
                    'severity': 'minor',
                    'message': f'Variable "{var_name}" appears to be unused.',
                    'pattern_match': 'unused_var_js'
                })
