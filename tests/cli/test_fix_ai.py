import click
from click.testing import CliRunner
from src.cli.commands.fix_ai import fix_ai
from unittest.mock import patch, MagicMock

@patch('src.cli.commands.fix_ai.Scanner')
@patch('src.cli.commands.fix_ai.LLMFactory')
@patch('src.cli.commands.fix_ai.ConfigLoader')
def test_fix_ai_command(mock_config_loader, mock_llm_factory, mock_scanner_cls):
    # Mock config
    mock_config = MagicMock()
    mock_config.load.return_value = {'languages': ['python']}
    mock_config_loader.return_value = mock_config

    # Mock scanner
    mock_scanner = MagicMock()
    mock_scanner.scan.return_value = {
        'issues': [
            {
                'id': 'test_rule',
                'type': 'green_violation',
                'file': 'test.py',
                'line': 10,
                'message': 'Violation found'
            }
        ]
    }
    mock_scanner_cls.return_value = mock_scanner

    # Mock LLM
    mock_llm = MagicMock()
    mock_llm.generate_fix.return_value = "Fixed code snippet"
    mock_llm.get_total_usage.return_value = MagicMock(total_tokens=100, cost=0.01)
    mock_llm_factory.get_provider.return_value = mock_llm

    # Mock file reading via builtins open (extract_snippet)
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a file with unique content to ensure snippet is unique
        # Ensure we have enough lines for line 10
        unique_content = "\n" * 9 + "violation = True # Line 10\n" + "\n" * 5
        with open("test.py", "w") as f:
            f.write(unique_content)

        result = runner.invoke(fix_ai, ['test.py', '--provider', 'mock', '--auto-apply'])

        assert result.exit_code == 0, result.output
        assert "Found 1 violations" in result.output
        assert "Starting AI fix process" in result.output
        assert "Proposed Fix (Diff):" in result.output
        assert "Fixed code snippet" in result.output
        assert "Fix applied successfully" in result.output
        assert "Token Usage: 100 tokens" in result.output

@patch('src.cli.commands.fix_ai.Scanner')
@patch('src.cli.commands.fix_ai.LLMFactory')
@patch('src.cli.commands.fix_ai.ConfigLoader')
def test_fix_ai_no_issues(mock_config_loader, mock_llm_factory, mock_scanner_cls):
    mock_config_loader.return_value.load.return_value = {'languages': ['python']}
    mock_scanner_cls.return_value.scan.return_value = {'issues': []}

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test.py", "w") as f:
            f.write("content")

        result = runner.invoke(fix_ai, ['test.py'])

    assert result.exit_code == 0, result.output
    assert "No violations found" in result.output
