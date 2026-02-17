"""
Unit tests for Codebase Emission Analyzer
"""

import pytest
import ast
from src.core.analyzer import (
    CodeComplexityAnalyzer,
    EmissionAnalyzer,
    ComplexityMetrics,
    analyze_code_complexity,
    estimate_codebase_emissions
)

class TestCodeComplexityAnalyzer:
    def test_empty_code(self):
        code = ""
        metrics = analyze_code_complexity("test.py", code)
        assert metrics.lines_of_code == 1
        assert metrics.cyclomatic_complexity == 1
        assert metrics.function_count == 0
        assert metrics.class_count == 0

    def test_basic_function(self):
        code = """
def hello():
    print("Hello")
"""
        metrics = analyze_code_complexity("test.py", code)
        assert metrics.function_count == 1
        assert metrics.class_count == 0
        assert metrics.cyclomatic_complexity == 1

    def test_cyclomatic_complexity(self):
        code = """
def complex(x):
    if x > 0:
        if x > 10:
            return 1
    elif x < 0:
        return -1
    else:
        return 0
"""
        metrics = analyze_code_complexity("test.py", code)
        # 1 (base) + 1 (if) + 1 (nested if) + 1 (elif) = 4
        assert metrics.cyclomatic_complexity == 4
        assert metrics.max_nesting_depth == 2

    def test_loops_complexity(self):
        code = """
def loops():
    for i in range(10):
        while True:
            break
"""
        metrics = analyze_code_complexity("test.py", code)
        # 1 (base) + 1 (for) + 1 (while) = 3
        assert metrics.cyclomatic_complexity == 3
        assert metrics.max_nesting_depth == 2
        assert metrics.loop_iterations_estimate >= 1010 # 10 (range) + 1000 (while)

    def test_recursion_detection(self):
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        metrics = analyze_code_complexity("test.py", code)
        assert metrics.function_count == 1
        assert 'factorial' in metrics.recursive_functions

    def test_class_detection(self):
        code = """
class MyClass:
    def method(self):
        pass
"""
        metrics = analyze_code_complexity("test.py", code)
        assert metrics.class_count == 1
        assert metrics.function_count == 1

    def test_io_detection(self):
        code = """
def read_file():
    with open('file.txt') as f:
        print(f.read())
"""
        metrics = analyze_code_complexity("test.py", code)
        assert metrics.has_io_operations is True

    def test_expensive_ops_detection(self):
        code = """
import re
def process():
    pattern = re.compile(r'\d+')
    data = sorted([3, 1, 2])
"""
        metrics = analyze_code_complexity("test.py", code)
        assert metrics.has_expensive_operations is True

    def test_async_function(self):
        code = """
async def fetch():
    pass
"""
        metrics = analyze_code_complexity("test.py", code)
        assert metrics.function_count == 1


class TestEmissionAnalyzer:
    def test_analyze_file_syntax_error(self):
        analyzer = EmissionAnalyzer()
        metrics = analyzer.analyze_file("test.py", "def broken(:")
        # Should return minimal metrics instead of crashing
        assert metrics.lines_of_code == 1
        assert metrics.cyclomatic_complexity == 1

    def test_estimate_emissions_basic(self):
        analyzer = EmissionAnalyzer()
        code = "print('hello')"
        metrics = analyzer.analyze_file("test.py", code)
        emissions = analyzer.estimate_emissions(metrics)
        assert emissions > 0

    def test_estimate_emissions_complexity_impact(self):
        analyzer = EmissionAnalyzer()

        simple_code = "x = 1"
        complex_code = """
def recursive(n):
    if n <= 0: return 0
    return recursive(n-1) + recursive(n-2)
"""
        simple_metrics = analyzer.analyze_file("simple.py", simple_code)
        complex_metrics = analyzer.analyze_file("complex.py", complex_code)

        simple_emissions = analyzer.estimate_emissions(simple_metrics)
        complex_emissions = analyzer.estimate_emissions(complex_metrics)

        assert complex_emissions > simple_emissions

    def test_memory_estimation(self):
        analyzer = EmissionAnalyzer()
        code = "import numpy as np; arr = np.array([1]*1000)"
        metrics = analyzer.analyze_file("test.py", code)
        assert metrics.memory_usage_estimate > 10.0 # Base is 10.0

    def test_analyze_codebase(self):
        files = {
            'test1.py': 'print("1")',
            'test2.py': 'print("2")',
            'ignore.txt': 'text'
        }
        total, per_file = estimate_codebase_emissions(files), {}
        # Need to call instance method to get per_file, helper only returns total?
        # estimate_codebase_emissions helper:
        # def estimate_codebase_emissions(file_contents: Dict[str, str]) -> float:
        #    analyzer = EmissionAnalyzer()
        #    total, _ = analyzer.analyze_codebase(file_contents)
        #    return total

        assert total > 0

        analyzer = EmissionAnalyzer()
        total, per_file = analyzer.analyze_codebase(files)
        assert len(per_file) == 2
        assert 'ignore.txt' not in per_file

    def test_add_to_analysis(self):
        analyzer = EmissionAnalyzer()
        e1 = analyzer.add_to_analysis("test1.py", "print(1)")
        e2 = analyzer.add_to_analysis("test2.py", "print(2)")

        assert analyzer.total_codebase_emissions > 0
        assert e1 > 0
        assert e2 > 0
        assert analyzer.total_codebase_emissions == pytest.approx(e1 + e2)

    def test_get_per_line_emissions(self):
        analyzer = EmissionAnalyzer()
        issues = [
            {'severity': 'high'},
            {'severity': 'low'}
        ]
        total_emissions = 100.0

        updated_issues = analyzer.get_per_line_emissions(issues, total_emissions)

        # High (3) + Low (1) = 4 parts
        # High = 3/4 * 100 = 75
        # Low = 1/4 * 100 = 25

        assert updated_issues[0]['codebase_emissions'] == 75.0
        assert updated_issues[1]['codebase_emissions'] == 25.0
