"""
JavaScript-specific detection strategies for green software violations.
"""

import re
from typing import List, Dict
from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_javascript
from src.utils.logger import logger
from src.utils.entropy import calculate_shannon_entropy
from .base_detector import BaseTreeSitterDetector

class JavaScriptASTDetector(BaseTreeSitterDetector):
    """AST-based detector for JavaScript using Tree-sitter."""

    def __init__(self, content: str, file_path: str, language_lib=tree_sitter_javascript):
        super().__init__(content, file_path, language_lib)

    def detect_all(self) -> List[Dict]:
        """Run all AST-based detectors."""
        if not self.tree:
            return []

        self._detect_simple_patterns()
        self._detect_magic_numbers()
        self._detect_loops()
        self._detect_dom_in_loops()
        self._detect_string_concatenation()
        self._detect_empty_blocks()
        self._detect_hardcoded_secrets()

        return self.violations

    def _detect_simple_patterns(self) -> None:
        """Detect simple patterns using a combined query."""
        query_scm = """
        ; console.time
        (call_expression
          function: (member_expression
            object: (identifier) @console_obj
            property: (property_identifier) @console_prop)
          (#eq? @console_obj "console")
          (#match? @console_prop "^(time|timeEnd)$")) @console_time

        ; console.log
        (call_expression
          function: (member_expression
            object: (identifier) @console_obj_log
            property: (property_identifier) @console_prop_log)
          (#eq? @console_obj_log "console")
          (#match? @console_prop_log "^(log|debug|info)$")) @console_log

        ; eval
        (call_expression
          function: (identifier) @eval_func
          (#eq? @eval_func "eval")) @eval_usage

        ; document.write
        (call_expression
          function: (member_expression
            object: (identifier) @doc_obj
            property: (property_identifier) @doc_prop)
          (#eq? @doc_obj "document")
          (#eq? @doc_prop "write")) @document_write

        ; innerHTML assignment
        (assignment_expression
          left: (member_expression
            property: (property_identifier) @inner_prop)
          (#eq? @inner_prop "innerHTML")) @inner_html

        ; momentjs require
        (call_expression
          function: (identifier) @req_func
          arguments: (arguments (string (string_fragment) @req_arg))
          (#eq? @req_func "require")
          (#match? @req_arg "moment")) @moment_require

        ; momentjs import
        (import_statement
            source: (string (string_fragment) @imp_source)
            (#match? @imp_source "moment")) @moment_import

        ; setInterval
        (call_expression
          function: (identifier) @interval_func
          (#eq? @interval_func "setInterval")) @set_interval

        ; alert/prompt/confirm (global)
        (call_expression
          function: (identifier) @alert_func
          (#match? @alert_func "^(alert|prompt|confirm)$")) @alert_global

        ; window.alert/prompt/confirm
        (call_expression
          function: (member_expression
            object: (identifier) @win_obj
            property: (property_identifier) @win_prop)
          (#eq? @win_obj "window")
          (#match? @win_prop "^(alert|prompt|confirm)$")) @alert_window

        ; readFileSync
        (call_expression
          function: (member_expression
            property: (property_identifier) @read_prop)
          (#match? @read_prop "readFileSync")) @read_sync

        ; XMLHttpRequest
        (new_expression
            constructor: (identifier) @xhr_cons
            (#eq? @xhr_cons "XMLHttpRequest")) @xhr

        ; Direct DOM query
        (call_expression
           function: (member_expression
             object: (identifier) @dom_obj
             property: (property_identifier) @dom_prop)
           (#eq? @dom_obj "document")
           (#match? @dom_prop "^(querySelector|getElementById)$")) @dom_query
        """

        try:
            query = Query(self.language, query_scm)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            reported_lines = set()

            for _, captures in matches:
                if not captures:
                    continue

                # Determine which rule matched
                rule_id = None
                severity = None
                message = None
                pattern_match = None
                node = None

                if 'console_time' in captures:
                    rule_id = 'console_time'
                    severity = 'minor'
                    message = 'console.time/timeEnd detected. Remove in production.'
                    pattern_match = 'console_time'
                    node = captures['console_time'][0]
                elif 'console_log' in captures:
                    rule_id = 'excessive_console_logging'
                    severity = 'minor'
                    message = 'Console logging detected. Remove in production.'
                    pattern_match = 'console_log'
                    node = captures['console_log'][0]
                elif 'eval_usage' in captures:
                    rule_id = 'eval_usage'
                    severity = 'critical'
                    message = 'Eval is a security risk and slow.'
                    pattern_match = 'eval_usage'
                    node = captures['eval_usage'][0]
                elif 'document_write' in captures:
                    rule_id = 'document_write'
                    severity = 'critical'
                    message = 'document.write blocks rendering.'
                    pattern_match = 'document_write'
                    node = captures['document_write'][0]
                elif 'inner_html' in captures:
                    rule_id = 'inner_html'
                    severity = 'major'
                    message = 'Avoid innerHTML. Use textContent or DOM methods.'
                    pattern_match = 'inner_html'
                    node = captures['inner_html'][0]
                elif 'moment_require' in captures or 'moment_import' in captures:
                    rule_id = 'momentjs_deprecated'
                    severity = 'major'
                    message = 'Moment.js is heavy. Use Day.js or Date.'
                    pattern_match = 'momentjs_deprecated'
                    node = captures.get('moment_require', captures.get('moment_import'))[0]
                elif 'set_interval' in captures:
                    rule_id = 'setInterval_animation'
                    severity = 'major'
                    message = 'Use requestAnimationFrame instead of setInterval.'
                    pattern_match = 'setInterval_animation'
                    node = captures['set_interval'][0]
                elif 'alert_global' in captures or 'alert_window' in captures:
                    rule_id = 'alert_usage'
                    severity = 'minor'
                    message = 'Native dialogs block the main thread.'
                    pattern_match = 'alert_usage'
                    node = captures.get('alert_global', captures.get('alert_window'))[0]
                elif 'read_sync' in captures or 'xhr' in captures:
                    rule_id = 'synchronous_io'
                    severity = 'major'
                    message = 'Synchronous I/O blocks the main thread. Use async APIs.'
                    pattern_match = 'sync_io_js'
                    node = captures.get('read_sync', captures.get('xhr'))[0]
                elif 'dom_query' in captures:
                    rule_id = 'unnecessary_dom_manipulation'
                    severity = 'major'
                    message = 'Direct DOM query/manipulation. Cache references.'
                    pattern_match = 'dom_query'
                    node = captures['dom_query'][0]

                if node:
                    line = node.start_point[0] + 1
                    # Simple deduplication by line and rule
                    key = f"{line}:{rule_id}"
                    if key not in reported_lines:
                        self.violations.append({
                            'id': rule_id,
                            'line': line,
                            'severity': severity,
                            'message': message,
                            'pattern_match': pattern_match
                        })
                        reported_lines.add(key)
        except Exception as e:
            logger.error(f"Error in combined pattern detection: {e}")

    def _detect_hardcoded_secrets(self) -> None:
        """Detect hardcoded secrets."""
        # Query for variable declarations, assignments, and object properties
        query_scm = """
        (variable_declarator
          name: (identifier) @name
          value: [(string) (template_string)] @val)

        (assignment_expression
          left: (identifier) @name
          right: [(string) (template_string)] @val)

        (pair
          key: (property_identifier) @name
          value: [(string) (template_string)] @val)
        """

        try:
            query = Query(self.language, query_scm)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            secret_patterns = ['password', 'secret', 'key', 'token', 'auth', 'credential', 'api_key']

            for _, captures in matches:
                name_node = captures.get('name', [])
                val_node = captures.get('val', [])

                if name_node and val_node:
                    name_text = name_node[0].text.decode('utf8')
                    val_text = val_node[0].text.decode('utf8')

                    # Remove quotes
                    clean_val = val_text.strip('"\'`')

                    if any(p in name_text.lower() for p in secret_patterns):
                        # Filter out empty strings, short strings, placeholders
                        if len(clean_val) > 8 and ' ' not in clean_val and not clean_val.startswith('<') and 'YOUR_' not in clean_val and not clean_val.startswith('process.env'):
                             self.violations.append({
                                'id': 'hardcoded_secret',
                                'line': name_node[0].start_point[0] + 1,
                                'severity': 'critical',
                                'message': f'Potential hardcoded secret in variable "{name_text}". Use environment variables.',
                                'pattern_match': 'hardcoded_secret_js'
                            })

                    # Check for high entropy strings regardless of variable name
                    # Only if the variable name isn't clearly safe
                    safe_patterns = ['hash', 'checksum', 'md5', 'sha', 'signature', 'id', 'uuid', 'class', 'style', 'color', 'url', 'path']
                    if not any(p in name_text.lower() for p in safe_patterns):
                        if len(clean_val) > 20 and ' ' not in clean_val and not clean_val.startswith('<'):
                             entropy = calculate_shannon_entropy(clean_val)
                             if entropy > 4.0:
                                 self.violations.append({
                                    'id': 'high_entropy_string',
                                    'line': val_node[0].start_point[0] + 1,
                                    'severity': 'critical',
                                    'message': f'High entropy string detected (entropy: {entropy:.2f}). Potential API key or secret.',
                                    'pattern_match': 'high_entropy_js'
                                })
        except Exception as e:
            logger.error(f"Error in secrets detection: {e}")

    def _detect_empty_blocks(self) -> None:
        """Detect empty blocks."""
        self._detect_empty_blocks_generic("(statement_block) @block")

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

    # _detect_deprecated_apis, _detect_inefficient_browser_apis, _detect_sync_io merged into _detect_simple_patterns

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

    def _detect_dom_in_loops(self) -> None:
        """Detect DOM manipulation inside loops."""
        # Note: Direct DOM query detection moved to _detect_simple_patterns

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
