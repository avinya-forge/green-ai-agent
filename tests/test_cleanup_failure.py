import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from src.cli.main import cli
import os

def test_scan_cleanup_on_failure():
    runner = CliRunner()

    with patch('src.core.git_operations.GitOperations.clone_and_checkout') as mock_clone:
        mock_clone.return_value = ('/tmp/dummy_repo', 'https://github.com/dummy/repo', 'main')

        with patch('src.core.scanner.main.Scanner.scan') as mock_scan:
            # Simulate a crash during scan
            mock_scan.side_effect = Exception("Scan crashed!")

            with patch('src.core.git_operations.GitOperations.cleanup_repo') as mock_cleanup:
                result = runner.invoke(cli, ['scan', '--git-url', 'https://github.com/dummy/repo'])

                assert result.exit_code == 1
                assert "Error during scan: Scan crashed!" in result.output

                # Cleanup should still be called
                mock_cleanup.assert_called_once_with('/tmp/dummy_repo')
