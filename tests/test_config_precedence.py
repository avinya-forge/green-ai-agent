import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from src.cli.commands.scan import scan

class TestConfigPrecedence:

    def test_cli_overrides_config(self, tmp_path):
        runner = CliRunner()

        # Create a dummy file in the temp path to scan
        scan_dir = tmp_path / "src"
        scan_dir.mkdir()
        (scan_dir / "test.py").write_text("print('hello')")

        with patch('src.cli.commands.scan.ConfigLoader') as MockLoader, \
             patch('src.cli.commands.scan.Scanner') as MockScanner, \
             patch('src.cli.commands.scan.GitOperations'), \
             patch('src.cli.commands.scan.ProjectManager'):

            # Setup mock config
            mock_loader_instance = MockLoader.return_value
            mock_config = {
                'languages': ['python'],
                'rules': {
                    'enabled': ['rule1'],
                    'disabled': ['rule2']
                }
            }
            mock_loader_instance.load.return_value = mock_config
            # scan.py accesses .config attribute directly for appending
            mock_loader_instance.config = mock_config

            # Mock get() method to handle dot notation
            def get_side_effect(key, default=None):
                if key == 'languages':
                    return ['python']
                if key == 'rules.disabled':
                    return mock_config['rules']['disabled']
                if key == 'rules.enabled':
                    return mock_config['rules']['enabled']
                return default

            mock_loader_instance.get.side_effect = get_side_effect

            # Setup mock scanner
            mock_scanner_instance = MockScanner.return_value
            mock_scanner_instance.config_loader = mock_loader_instance
            mock_scanner_instance.scan.return_value = {
                'issues': [],
                'codebase_emissions': 0,
                'scanning_emissions': 0,
                'per_file_emissions': {}
            }

            # Run CLI with overrides, pointing to the temp directory
            result = runner.invoke(scan, [str(scan_dir), '--disable-rule', 'rule1', '--enable-rule', 'rule3'])

            if result.exit_code != 0:
                print(result.output)

            assert result.exit_code == 0

            # Verify config was updated
            assert 'rule1' in mock_config['rules']['disabled']
            assert 'rule3' in mock_config['rules']['enabled']

            # Also verify rule2 is still there
            assert 'rule2' in mock_config['rules']['disabled']
