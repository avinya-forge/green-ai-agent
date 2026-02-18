import pytest
import requests
from unittest.mock import patch, MagicMock
from src.standards.registry import StandardsRegistry, StandardRule
from src.standards.sources import GSFSource, EcoCodeSource

@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get

def test_gsf_source_fetch_success(mock_requests_get):
    """Test successful fetching from GSF source."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    - id: gsf-001
      title: Test Rule
      description: A test rule
      severity: critical
      languages: [python]
      pattern: test
      remediation: fix it
    """
    mock_requests_get.return_value = mock_response

    source = GSFSource()
    rules = source.fetch()

    assert len(rules) == 1
    assert rules[0].id == 'gsf-001'
    assert rules[0].name == 'Test Rule'
    assert rules[0].source == 'GSF'

def test_ecocode_source_fetch_success(mock_requests_get):
    """Test successful fetching from EcoCode source."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    {
        "rules": [
            {
                "id": "eco-001",
                "name": "Eco Rule",
                "summary": "Save energy",
                "severity": "minor",
                "pattern": "foo",
                "fix": "bar"
            }
        ]
    }
    """
    mock_requests_get.return_value = mock_response

    source = EcoCodeSource()
    rules = source.fetch()

    assert len(rules) == 1
    assert rules[0].id == 'eco-001'
    assert rules[0].source == 'ecoCode'

def test_fetch_failure(mock_requests_get):
    """Test handling of fetch failures."""
    mock_requests_get.side_effect = requests.RequestException("Network error")

    source = GSFSource()
    rules = source.fetch()

    assert rules == []

def test_registry_sync(mock_requests_get):
    """Test the sync_standards method in registry."""
    # Mock GSF success
    mock_response_gsf = MagicMock()
    mock_response_gsf.status_code = 200
    mock_response_gsf.text = "- id: gsf-new\n  title: New Rule"

    # Mock EcoCode failure (empty)
    mock_response_eco = MagicMock()
    mock_response_eco.status_code = 404

    def side_effect(url, timeout=10):
        if "Green-Software-Foundation" in url:
            return mock_response_gsf
        return mock_response_eco

    mock_requests_get.side_effect = side_effect

    registry = StandardsRegistry()

    # Initial state
    assert 'gsf' in registry.standards
    # original_count = len(registry.standards['gsf'])

    # Sync
    result = registry.sync_standards()

    # GSF should update (mock returns 1 rule)
    assert result['gsf'] is True
    assert len(registry.standards['gsf']) == 1
    assert registry.standards['gsf'][0].id == 'gsf-new'

    # EcoCode should fail/not update
    assert result['ecocode'] is False
