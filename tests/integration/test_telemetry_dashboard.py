import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.ui.app_fastapi import app

client = TestClient(app)

@pytest.fixture
def mock_telemetry_service():
    with patch('src.ui.app_fastapi.TelemetryService') as MockService:
        instance = MockService.return_value
        instance.get_all_events.return_value = [
            {
                "event_type": "scan_complete",
                "timestamp": "2023-10-26T10:00:00Z",
                "project_id": "proj1",
                "payload": {
                    "violations_by_severity": {"high": 1, "low": 2},
                    "violations_by_rule": {"rule1": 1, "rule2": 2}
                }
            }
        ]
        yield instance

def test_telemetry_endpoint(mock_telemetry_service):
    response = client.get("/api/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert len(data['events']) == 1
    assert data['events'][0]['event_type'] == 'scan_complete'
    assert data['events'][0]['payload']['violations_by_severity']['high'] == 1
