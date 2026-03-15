from typing import List, Dict
from tree_sitter import Language
import tree_sitter_c_sharp
from src.core.detectors.base_detector import BaseTreeSitterDetector


class CSharpASTDetector(BaseTreeSitterDetector):
    """
    Detector for C# files using tree-sitter-c-sharp.
    """

    _CACHED_LANGUAGE = None

    def __init__(self, content: str, file_path: str):
        if CSharpASTDetector._CACHED_LANGUAGE is None:
            CSharpASTDetector._CACHED_LANGUAGE = Language(tree_sitter_c_sharp.language())

        super().__init__(content, file_path, CSharpASTDetector._CACHED_LANGUAGE)

    def detect_all(self) -> List[Dict]:
        """
        Run all C# AST-based rules.
        """
        self.violations = []

        self._detect_empty_blocks()
        self._detect_blocking_async_calls()
        self._detect_inefficient_string_concatenation_in_loops()
        self._detect_multiple_linq_iterations()

        return self.violations

    def _detect_empty_blocks(self):
        query = "(block) @block"
        self._detect_empty_blocks_generic(query)

    def _detect_blocking_async_calls(self):
        # [CS-003] blocking async calls (.Result/.Wait)
        query = """
        (member_access_expression
            name: (identifier) @method
            (#match? @method "^(Result|Wait)$")
        ) @blocking
        """
        self._run_query(
            query,
            'blocking_async_calls',
            'major',
            'Blocking async call detected (.Result or .Wait). Use await instead.',
            'blocking_async_call'
        )

    def _detect_inefficient_string_concatenation_in_loops(self):
        # [CS-004] inefficient string concatenation in loops
        # NOTE: Using a simpler match. We look for assignment_expression
        # with operator += where left is an identifier, inside a loop.
        # Tree-sitter C# syntax for `body: (block ...)` might differ or have
        # intermediate nodes (like statement wrappers). We use descendants `(_)` to match inside.
        query = """
        (for_statement
            (block
                (_) *
                (expression_statement
                    (assignment_expression
                        (identifier)
                        "+="
                    )
                )
            )
        ) @concat

        (while_statement
            (block
                (_) *
                (expression_statement
                    (assignment_expression
                        (identifier)
                        "+="
                    )
                )
            )
        ) @concat

        (foreach_statement
            (block
                (_) *
                (expression_statement
                    (assignment_expression
                        (identifier)
                        "+="
                    )
                )
            )
        ) @concat
        """
        self._run_query(
            query,
            'string_concatenation_in_loop',
            'major',
            'Inefficient string concatenation inside loop. Use StringBuilder.',
            'string_concatenation_in_loop'
        )

    def _detect_multiple_linq_iterations(self):
        # [CS-005] multiple LINQ iterations (ToList inside loop)
        # Match `query.ToList()` where `ToList` is the right side of member_access_expression
        query = """
        (for_statement
            (block
                (_) *
                (local_declaration_statement
                    (variable_declaration
                        (variable_declarator
                            (invocation_expression
                                (member_access_expression
                                    name: (identifier) @method
                                    (#match? @method "^(ToList|ToArray|ToDictionary|ToHashSet)$")
                                )
                            )
                        )
                    )
                )
            )
        ) @linq

        (while_statement
            (block
                (_) *
                (local_declaration_statement
                    (variable_declaration
                        (variable_declarator
                            (invocation_expression
                                (member_access_expression
                                    name: (identifier) @method
                                    (#match? @method "^(ToList|ToArray|ToDictionary|ToHashSet)$")
                                )
                            )
                        )
                    )
                )
            )
        ) @linq

        (foreach_statement
            (block
                (_) *
                (local_declaration_statement
                    (variable_declaration
                        (variable_declarator
                            (invocation_expression
                                (member_access_expression
                                    name: (identifier) @method
                                    (#match? @method "^(ToList|ToArray|ToDictionary|ToHashSet)$")
                                )
                            )
                        )
                    )
                )
            )
        ) @linq
        """
        self._run_query(
            query,
            'multiple_linq_iterations',
            'major',
            'Multiple LINQ iterations inside loop. Materialize collection outside loop.',
            'multiple_linq_iterations'
        )
