import os
import pytest
from click.testing import CliRunner
from src.cli.main import cli
import tempfile
from pathlib import Path

class TestCLIProfile:
    def test_perf_profile_flag(self):
        """Test that --perf-profile flag generates stats file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # We need to run scan on a small file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello')")

            result = runner.invoke(cli, ['scan', str(test_file), '--perf-profile'])

            assert result.exit_code == 0
            assert "Running with cProfile enabled" in result.output
            assert "Profile stats saved to" in result.output

            stats_file = Path('output/scanner_profile.stats')
            assert stats_file.exists()

            # Cleanup handled by teardown or just leave it (it's in output/)
