import pytest
from src.core.analyzer import CodeComplexityAnalyzer, ComplexityMetrics, EmissionAnalyzer
import ast

def test_cognitive_complexity_flat():
    code = """
def flat_function():
    if True:
        pass
    for i in range(10):
        pass
    while False:
        pass
"""
    tree = ast.parse(code)
    analyzer = CodeComplexityAnalyzer()
    analyzer.visit(tree)

    # Base CC is 1, plus 3 decision points = 4
    assert analyzer.cyclomatic_complexity == 4
    # All decisions are at depth 1 (relative to function, but our tracking just increments current_depth before visit).
    # Let's trace it: Function def (depth 0). visit_If increments current_depth to 1. But cognitive penalty is applied *before* increment.
    # Wait, the code says:
    # self.cognitive_complexity += self.current_depth
    # self.current_depth += 1
    # So if it's top level inside a function, `current_depth` is 0.
    # Let's check the code: FunctionDef doesn't increment current_depth.
    assert analyzer.cognitive_complexity == 0

def test_cognitive_complexity_nested():
    code = """
def nested_function():
    if True:
        for i in range(10):
            while False:
                pass
"""
    tree = ast.parse(code)
    analyzer = CodeComplexityAnalyzer()
    analyzer.visit(tree)

    assert analyzer.cyclomatic_complexity == 4
    # If (depth 0) -> cog += 0, depth becomes 1
    #  For (depth 1) -> cog += 1, depth becomes 2
    #   While (depth 2) -> cog += 2, depth becomes 3
    # Total cognitive: 3
    assert analyzer.cognitive_complexity == 3

def test_complexity_metrics_calculation():
    metrics = ComplexityMetrics(
        lines_of_code=1000,
        cyclomatic_complexity=50,
        cognitive_complexity=30,
        max_nesting_depth=10,
        function_count=10,
        class_count=2,
        recursive_functions=set(),
        memory_usage_estimate=10.0,
        loop_iterations_estimate=1000,
        has_io_operations=False,
        has_expensive_operations=False
    )
    score = metrics.calculate_complexity_score()

    # loc = 20
    # cc = 20
    # cog = 10
    # depth = 10
    # loop = (1000/100000)*20 = 0.2
    # entity = (12/100)*10 = 1.2
    # total = 61.4
    assert 61.3 < score < 61.5
