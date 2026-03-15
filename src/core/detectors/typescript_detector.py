"""
TypeScript-specific detection strategies for green software violations.
"""

from typing import List, Dict
from tree_sitter import Query, QueryCursor
import tree_sitter_typescript
from src.utils.logger import logger
from .javascript_detector import JavaScriptASTDetector


class TypeScriptASTDetector(JavaScriptASTDetector):
    """AST-based detector for TypeScript using Tree-sitter."""

    def __init__(self, content: str, file_path: str):
        language_lib = tree_sitter_typescript.language_typescript()
        if file_path.endswith('.tsx'):
            language_lib = tree_sitter_typescript.language_tsx()

        super().__init__(content, file_path, language_lib)

    def detect_all(self) -> List[Dict]:
        """Run all AST-based detectors."""
        if not self.tree:
            return []

        # Run inherited JS detectors (populates self.violations)
        super().detect_all()

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
        query_scm = """
        (enum_declaration) @enum
        """
        if not self.tree:
            return

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
                        self._add_violation(
                            node,
                            'prefer_const_enum',
                            'minor',
                            'Prefer "const enum" over "enum" to reduce bundle size.',
                            'enum_usage'
                        )
        except Exception as e:
            logger.error(f"Error in enum detection: {e}")
