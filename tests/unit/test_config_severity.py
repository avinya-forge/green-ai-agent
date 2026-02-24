import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.core.scanner.worker import scan_file_worker

@pytest.fixture
def mock_detect_violations():
    with patch('src.core.scanner.worker.detect_violations') as mock:
        yield mock

@pytest.fixture
def mock_remediation_engine():
    with patch('src.core.scanner.worker.RemediationEngine') as mock:
        mock.return_value.get_suggestion.return_value = "Suggestion"
        yield mock

@pytest.fixture
def mock_emission_analyzer():
    with patch('src.core.scanner.worker.EmissionAnalyzer') as mock:
        mock.return_value.analyze_file.return_value = {}
        mock.return_value.estimate_emissions.return_value = 0.001
        yield mock

def test_severity_override(mock_detect_violations, mock_remediation_engine, mock_emission_analyzer):
    # Setup
    file_path = "test.py"
    language = "python"

    # Define a rule with default severity 'medium'
    rules = [{
        'id': 'test_rule',
        'severity': 'medium',
        'name': 'Test Rule',
        'remediation': 'Fix it',
        'effort': 'Low',
        'tags': ['test']
    }]

    # Configure override to 'critical'
    config = {
        'rules': {
            'enabled': ['test_rule'],
            'severity': {
                'test_rule': 'critical'
            }
        }
    }

    # Mock detection
    mock_detect_violations.return_value = [{
        'id': 'test_rule',
        'line': 1,
        'message': 'Violation found'
    }]

    # Mock file open
    with patch('builtins.open', mock_open(read_data="code = 1")):
        result = scan_file_worker(file_path, language, config, rules)

    # Verify
    assert len(result['issues']) == 1
    issue = result['issues'][0]
    assert issue['id'] == 'test_rule'
    assert issue['severity'] == 'critical' # Should be overridden

def test_severity_no_override(mock_detect_violations, mock_remediation_engine, mock_emission_analyzer):
    # Setup
    file_path = "test.py"
    language = "python"

    rules = [{
        'id': 'test_rule',
        'severity': 'medium',
        'name': 'Test Rule'
    }]

    config = {
        'rules': {
            'enabled': ['test_rule'],
            'severity': {} # No override
        }
    }

    mock_detect_violations.return_value = [{
        'id': 'test_rule',
        'line': 1,
        'message': 'Violation found'
    }]

    with patch('builtins.open', mock_open(read_data="code = 1")):
        result = scan_file_worker(file_path, language, config, rules)

    assert result['issues'][0]['severity'] == 'medium'
