import pytest
from src.core.analyzer import EmissionAnalyzer, ComplexityMetrics


def test_cognitive_complexity_basic():
    analyzer = EmissionAnalyzer()
    code = """


def foo(x):
    if x > 0:           # +1
        if x < 10:      # +2 (nesting=1)
            return True
    return False
"""
    metrics = analyzer.analyze_file("test.py", code)
    assert metrics.cognitive_complexity == 3


def test_cognitive_complexity_bool_ops():
    analyzer = EmissionAnalyzer()
    code = "if a and b or c: pass"  # 1 (if) + 2 (bool ops) = 3
    metrics = analyzer.analyze_file("test.py", code)
    assert metrics.cognitive_complexity == 3


def test_cognitive_complexity_nesting():
    analyzer = EmissionAnalyzer()
    code = """
for i in range(10):     # +1
    while True:         # +2 (nesting=1)
        if True:        # +3 (nesting=2)
            try:        # +1 (nesting=3, but except is what counts usually, let us see our impl)
                pass
            except:     # +4 (nesting=3)
                pass
"""
    # Our impl: for (+1), while (+2), if (+3), except (+4). 1+2+3+4 = 10.
    metrics = analyzer.analyze_file("test.py", code)
    assert metrics.cognitive_complexity == 10


def test_complexity_score_calculation():
    metrics = ComplexityMetrics(
        lines_of_code=100,
        cyclomatic_complexity=5,
        max_nesting_depth=2,
        function_count=1,
        class_count=0,
        recursive_functions=set(),
        memory_usage_estimate=10.0,
        loop_iterations_estimate=100,
        has_io_operations=False,
        has_expensive_operations=False,
        cognitive_complexity=10
    )
    score = metrics.calculate_complexity_score()
    # loc: 2, cc: 2.5, depth: 3, loop: 0.02, entity: 0.1, cog: 4. Total ~11.62
    assert score == pytest.approx(11.62, 0.1)
