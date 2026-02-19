"""
TypeScript-specific detection strategies for green software violations.
"""

from typing import List, Dict
from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_typescript
from src.utils.logger import logger
from .javascript_detector import JavaScriptASTDetector

class TypeScriptASTDetector(JavaScriptASTDetector):
    """AST-based detector for TypeScript using Tree-sitter."""

    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.violations = []
        self.tree = None
        self.language = None

        try:
            # Determine if TS or TSX based on extension
            if file_path.endswith('.tsx'):
                self.language = Language(tree_sitter_typescript.language_tsx())
            else:
                self.language = Language(tree_sitter_typescript.language_typescript())

            self.parser = Parser(self.language)
            self.tree = self.parser.parse(bytes(self.content, "utf8"))
        except Exception as e:
            logger.error(f"Error initializing Tree-sitter for {file_path}: {e}")

    def detect_all(self) -> List[Dict]:
        """Run all AST-based detectors."""
        if not self.tree:
            return []

        # Run inherited JS detectors
        # We call the internal methods directly because super().detect_all()
        # calls them on self, which is this instance.
        # However, some JS queries might need slight adjustment if the AST differs significantly.
        # Generally, TS AST is a superset, so JS queries should work.

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

        # Run TS-specific detectors
        self._detect_any_type()
        self._detect_enum()

        return self.violations

    def _detect_any_type(self) -> None:
        """Detect usage of 'any' type."""
        query_scm = """
        (predefined_type) @type
        (#eq? @type "any")
        """
        self._run_query(query_scm, 'any_type_usage', 'major',
                       'Avoid using "any" type. It defeats the purpose of TypeScript and can hide inefficiencies.', 'any_type')

    def _detect_enum(self) -> None:
        """Detect usage of regular enum (prefer const enum)."""
        # (enum_declaration (const))?
        # Regular enum: (enum_declaration) but without 'const' keyword
        # Tree-sitter structure for enum:
        # (enum_declaration name: (identifier) body: (enum_body))
        # If it is const enum: (enum_declaration (const) ...) or similar.
        # Let's check the grammar or just use a negative lookahead if possible, or check children.

        query_scm = """
        (enum_declaration) @enum
        """
        try:
            query = Query(self.language, query_scm)
            cursor = QueryCursor(query)
            matches = cursor.matches(self.tree.root_node)

            for _, captures in matches:
                nodes = captures.get('enum', [])
                for node in nodes:
                    # Check if 'const' keyword is present among children
                    is_const = False
                    for child in node.children:
                        if child.type == 'const':
                            is_const = True
                            break

                    if not is_const:
                        line = node.start_point[0] + 1
                        self.violations.append({
                            'id': 'prefer_const_enum',
                            'line': line,
                            'severity': 'minor',
                            'message': 'Prefer "const enum" over "enum" to reduce bundle size.',
                            'pattern_match': 'enum_usage'
                        })
        except Exception as e:
            logger.error(f"Error in enum detection: {e}")
