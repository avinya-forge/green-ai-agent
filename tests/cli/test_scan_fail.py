import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from src.cli.commands.scan import scan

@pytest.fixture
def mock_scanner():
    with patch('src.cli.commands.scan.Scanner') as MockScanner:
        instance = MockScanner.return_value
        instance.scan.return_value = {
            'issues': [],
            'scanning_emissions': 0.0,
            'codebase_emissions': 0.0,
            'runtime_metrics': {}
        }
        # Config loader mock
        instance.config_loader = MagicMock()
        instance.config_loader.get.return_value = []
        instance.config_loader.config = {'rules': {'enabled': [], 'disabled': []}}
        yield instance

def test_scan_fail_on_critical(mock_scanner):
    runner = CliRunner()

    # Mock issues
    mock_scanner.scan.return_value['issues'] = [
        {'id': 'issue1', 'severity': 'critical', 'message': 'Critical issue'}
    ]

    with runner.isolated_filesystem():
        # Create dummy file to scan
        with open("test.py", "w") as f:
            f.write("pass")

        result = runner.invoke(scan, ['test.py', '--fail-on', 'critical'])

        assert result.exit_code == 1
        assert "[FAILURE] Scan failed due to violations of severity 'critical' or higher." in result.output

def test_scan_pass_on_low(mock_scanner):
    runner = CliRunner()

    # Mock issues - only low severity
    mock_scanner.scan.return_value['issues'] = [
        {'id': 'issue1', 'severity': 'low', 'message': 'Low issue'}
    ]

    with runner.isolated_filesystem():
        with open("test.py", "w") as f:
            f.write("pass")

        # Fail on critical -> should pass
        result = runner.invoke(scan, ['test.py', '--fail-on', 'critical'])

        assert result.exit_code == 0
        assert "[FAILURE]" not in result.output

def test_scan_fail_on_medium_with_high(mock_scanner):
    runner = CliRunner()

    # Mock issues - high severity (higher than medium)
    mock_scanner.scan.return_value['issues'] = [
        {'id': 'issue1', 'severity': 'high', 'message': 'High issue'}
    ]

    with runner.isolated_filesystem():
        with open("test.py", "w") as f:
            f.write("pass")

        result = runner.invoke(scan, ['test.py', '--fail-on', 'medium'])

        assert result.exit_code == 1
        assert "[FAILURE] Scan failed due to violations of severity 'medium' or higher." in result.output

def test_scan_fail_on_major_mapping(mock_scanner):
    runner = CliRunner()

    # Mock issues - major severity (mapped to high)
    mock_scanner.scan.return_value['issues'] = [
        {'id': 'issue1', 'severity': 'major', 'message': 'Major issue'}
    ]

    with runner.isolated_filesystem():
        with open("test.py", "w") as f:
            f.write("pass")

        # Fail on high -> should fail because major >= high (both mapped to 3)
        # Wait, my logic map: major->3, high->3. Fail on 'high' (3) -> >= 3 -> True.
        result = runner.invoke(scan, ['test.py', '--fail-on', 'high'])

        assert result.exit_code == 1
        assert "[FAILURE] Scan failed" in result.output

def test_scan_fail_on_minor_fail_low(mock_scanner):
    runner = CliRunner()

    # Mock issues - minor (mapped to 1/low)
    mock_scanner.scan.return_value['issues'] = [
        {'id': 'issue1', 'severity': 'minor', 'message': 'Minor issue'}
    ]

    with runner.isolated_filesystem():
        with open("test.py", "w") as f:
            f.write("pass")

        # Fail on low (1) -> minor (1) >= 1 -> True
        result = runner.invoke(scan, ['test.py', '--fail-on', 'low'])

        assert result.exit_code == 1
