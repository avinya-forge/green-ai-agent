import pytest
import timeit
from src.core.detectors.go_detector import GoASTDetector
from src.core.detectors.python_detector import PythonViolationDetector
import ast

def test_go_ast_performance_benchmark():
    go_code = """
    package main
    import "fmt"
    func main() {
        s := ""
        for i := 0; i < 1000; i++ {
            s += "a"
        }
        fmt.Println(s)
    }
    """

    py_code = """
def main():
    s = ""
    for i in range(1000):
        s += "a"
    print(s)
    """

    def run_go():
        detector = GoASTDetector(go_code, "main.go")
        detector.detect_all()

    def run_py():
        tree = ast.parse(py_code)
        detector = PythonViolationDetector(py_code, "main.py")
        detector.visit(tree)

    go_time = timeit.timeit(run_go, number=10)
    py_time = timeit.timeit(run_py, number=10)

    print(f"\nGoASTDetector time (10 runs): {go_time:.4f}s")
    print(f"PythonViolationDetector time (10 runs): {py_time:.4f}s")
    print(f"Ratio (Go/Py): {go_time / py_time:.2f}")

    # The spec doesn't require a strict assert on speed, but just a benchmark suite
    # We will assert that both run successfully and the benchmark completes.
    assert go_time > 0
    assert py_time > 0
