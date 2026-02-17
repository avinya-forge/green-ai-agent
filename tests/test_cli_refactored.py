import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from src.cli.main import cli

class TestCLIRefactored:
    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Green AI Software Analyzer' in result.output
        assert 'scan' in result.output
        assert 'project' in result.output
        assert 'dashboard' in result.output

    @patch('src.cli.commands.scan.Scanner')
    @patch('src.cli.commands.scan.ConfigLoader')
    @patch('src.cli.commands.scan.set_last_scan_results')
    def test_scan_command(self, mock_set_last, mock_config, mock_scanner):
        # Mock setup
        mock_scanner_instance = MagicMock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.scan.return_value = {'issues': [], 'scanning_emissions': 0, 'codebase_emissions': 0}

        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.load.return_value = {'languages': ['python']}

        runner = CliRunner()
        # Create a dummy file to scan
        with runner.isolated_filesystem():
            with open('test.py', 'w') as f:
                f.write('print("hello")')

            result = runner.invoke(cli, ['scan', 'test.py'])

            assert result.exit_code == 0
            assert 'Scanning' in result.output
            assert 'Scan complete' in result.output
            mock_scanner_instance.scan.assert_called_once()

    @patch('src.cli.commands.project.ProjectManager')
    def test_project_add(self, mock_pm):
        mock_pm_instance = MagicMock()
        mock_pm.return_value = mock_pm_instance
        mock_pm_instance.get_project.return_value = None
        mock_pm_instance.add_project.return_value = MagicMock(id='123', branch='main')

        runner = CliRunner()
        result = runner.invoke(cli, ['project', 'add', 'test-project', 'https://github.com/test/repo'])

        assert result.exit_code == 0
        assert 'Project added: test-project' in result.output
        mock_pm_instance.add_project.assert_called_once()

    @patch('src.ui.server.run_dashboard')
    def test_dashboard_command(self, mock_run):
        runner = CliRunner()
        # Mock sys.argv if needed, but click handles it
        result = runner.invoke(cli, ['dashboard'])

        assert result.exit_code == 0
        assert 'Launching dashboard' in result.output
        mock_run.assert_called_once()
