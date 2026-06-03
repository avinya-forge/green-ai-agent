import pytest
from unittest.mock import patch, MagicMock
from src.core.sca.osv_client import OSVClient

@patch('requests.post')
def test_query_vulnerability_found(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'vulns': [{'id': 'CVE-123', 'summary': 'Test vuln'}]}
    mock_post.return_value = mock_response

    client = OSVClient()
    vulns = client.query_vulnerability('fastapi', '0.100.0')

    assert len(vulns) == 1
    assert vulns[0]['id'] == 'CVE-123'

@patch('requests.post')
def test_query_vulnerability_none(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response

    client = OSVClient()
    vulns = client.query_vulnerability('secure-pkg', '1.0.0')

    assert len(vulns) == 0

def test_query_vulnerability_unknown_version():
    client = OSVClient()
    vulns = client.query_vulnerability('pkg', 'unknown')
    assert len(vulns) == 0
