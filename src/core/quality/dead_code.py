"""
Dead code detection for Green AI.
Identifies unused functions, classes, and variables to reduce code bloat and energy footprint.
"""

import ast
from typing import List, Dict, Set


class DeadCodeDetector(ast.NodeVisitor):
    """
    AST visitor to identify potentially unused code.
    """

    def __init__(self):
        self.defined_functions: Dict[str, int] = {} # name -> line
        self.called_functions: Set[str] = set()
        self.defined_classes: Dict[str, int] = {}
        self.used_classes: Set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if not node.name.startswith('_'): # Ignore private/internal
            self.defined_functions[node.name] = node.lineno
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        if not node.name.startswith('_'):
            self.defined_classes[node.name] = node.lineno
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            self.called_functions.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.called_functions.add(node.func.attr)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            self.used_classes.add(node.id)
            self.called_functions.add(node.id)
        self.generic_visit(node)

    def get_dead_code(self) -> List[Dict]:
        """Return list of unused definitions."""
        dead = []

        # Unused functions
        for name, line in self.defined_functions.items():
            if name not in self.called_functions and name not in ('main', 'app'):
                dead.append({
                    'id': 'unused_function',
                    'type': 'quality',
                    'severity': 'medium',
                    'message': f"Function '{name}' is defined but never called.",
                    'line': line,
                    'name': name
                })

        # Unused classes
        for name, line in self.defined_classes.items():
            if name not in self.used_classes:
                dead.append({
                    'id': 'unused_class',
                    'type': 'quality',
                    'severity': 'medium',
                    'message': f"Class '{name}' is defined but never used.",
                    'line': line,
                    'name': name
                })

        return dead
