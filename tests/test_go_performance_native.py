import subprocess
import os
import pytest

def test_native_go_benchmark():
    # Verify that the native Go benchmark exists
    benchmark_dir = os.path.join("tests", "performance_go")
    assert os.path.exists(benchmark_dir)
    assert os.path.exists(os.path.join(benchmark_dir, "benchmark_test.go"))
    assert os.path.exists(os.path.join(benchmark_dir, "go.mod"))

    # Run the native Go benchmark
    result = subprocess.run(
        ["go", "test", "-bench=."],
        cwd=benchmark_dir,
        capture_output=True,
        text=True
    )

    # Check that it completed successfully
    assert result.returncode == 0
    assert "BenchmarkGoASTParse" in result.stdout
