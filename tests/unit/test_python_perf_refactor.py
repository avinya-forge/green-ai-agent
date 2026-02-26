import ast
import pytest
from src.core.detectors.python_detector import PythonViolationDetector

def test_io_in_loop():
    code = """
for i in range(10):
    print(i)
    with open('file.txt', 'r') as f:
        f.read()
"""
    detector = PythonViolationDetector(code, "test.py")
    violations = detector.detect_all()

    # Expect io_in_loop violation for open() and read()
    io_violations = [v for v in violations if v['id'] == 'io_in_loop']
    assert len(io_violations) >= 1
    assert io_violations[0]['pattern_match'] == 'io_operation_in_loop'

def test_unnecessary_computation_in_loop():
    code = """
for i in range(10):
    x = len([1, 2, 3])
    y = range(100)
"""
    detector = PythonViolationDetector(code, "test.py")
    violations = detector.detect_all()

    # Expect unnecessary_computation for len and range
    comp_violations = [v for v in violations if v['id'] == 'unnecessary_computation']
    assert len(comp_violations) >= 2

def test_inefficient_lookup_in_loop():
    code = """
my_list = [1, 2, 3]
for i in range(10):
    if i in my_list:
        pass
"""
    detector = PythonViolationDetector(code, "test.py")
    violations = detector.detect_all()

    # Expect inefficient_lookup
    lookup_violations = [v for v in violations if v['id'] == 'inefficient_lookup']
    assert len(lookup_violations) == 1

def test_nested_loops_io():
    code = """
for i in range(10):
    for j in range(10):
        requests.get('http://example.com')
"""
    detector = PythonViolationDetector(code, "test.py")
    violations = detector.detect_all()

    # io_in_loop should be detected
    io_violations = [v for v in violations if v['id'] == 'io_in_loop']
    assert len(io_violations) >= 1

    # blocking_io should also be detected
    blocking_violations = [v for v in violations if v['id'] == 'blocking_io']
    assert len(blocking_violations) >= 1

def test_no_loop_no_violation():
    code = """
requests.get('http://example.com')
x = len([1, 2, 3])
if 1 in [1, 2]:
    pass
"""
    detector = PythonViolationDetector(code, "test.py")
    violations = detector.detect_all()

    io_violations = [v for v in violations if v['id'] == 'io_in_loop']
    assert len(io_violations) == 0

    comp_violations = [v for v in violations if v['id'] == 'unnecessary_computation']
    assert len(comp_violations) == 0

    lookup_violations = [v for v in violations if v['id'] == 'inefficient_lookup']
    assert len(lookup_violations) == 0
