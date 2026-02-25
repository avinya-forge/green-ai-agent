import pytest
import json
import os
from fastapi.testclient import TestClient
from src.ui.app_fastapi import app
from src.core.telemetry.service import TelemetryService

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_telemetry_file(tmp_path):
    """Mock the telemetry file path to a temporary file."""
    # Create a temporary file path
    telemetry_file = tmp_path / "telemetry.jsonl"

    # Patch the storage path in TelemetryService
    service = TelemetryService()
    original_path = service.storage_path
    service.storage_path = telemetry_file

    # Create some dummy data
    event1 = {
        "event_id": "1",
        "timestamp": "2023-10-26T10:00:00Z",
        "event_type": "scan_complete",
        "payload": {
            "project_id": "proj1",
            "violations_by_severity": {"high": 1, "low": 2},
            "violations_by_rule": {"rule1": 1, "rule2": 2}
        }
    }
    event2 = {
        "event_id": "2",
        "timestamp": "2023-10-27T10:00:00Z",
        "event_type": "error",
        "payload": {"message": "something went wrong"}
    }

    with open(telemetry_file, 'w') as f:
        f.write(json.dumps(event1) + '\n')
        f.write(json.dumps(event2) + '\n')

    yield telemetry_file

    # Cleanup
    service.storage_path = original_path

def test_get_telemetry_api(client, mock_telemetry_file):
    """Test the GET /api/telemetry endpoint."""
    response = client.get("/api/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "events" in data
    assert len(data["events"]) == 2

    events = data["events"]
    assert events[0]["event_type"] == "scan_complete"
    assert events[1]["event_type"] == "error"
    assert events[0]["payload"]["project_id"] == "proj1"

def test_telemetry_service_get_all_events(mock_telemetry_file):
    """Test the TelemetryService.get_all_events method directly."""
    service = TelemetryService()
    events = service.get_all_events()
    assert len(events) == 2
    assert events[0]["event_id"] == "1"

def test_telemetry_api_empty_file(client, tmp_path):
    """Test API when file doesn't exist."""
    # Ensure service points to non-existent file
    service = TelemetryService()
    original_path = service.storage_path
    service.storage_path = tmp_path / "non_existent.jsonl"

    try:
        response = client.get("/api/telemetry")
        assert response.status_code == 200
        data = response.json()
        assert data["events"] == []
    finally:
        service.storage_path = original_path
