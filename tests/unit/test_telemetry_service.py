import pytest
import os
import json
import shutil
from pathlib import Path
from src.core.telemetry.service import TelemetryService
from src.core.telemetry.schemas import TelemetryEvent

# Helper to clear singleton instance
def reset_telemetry_service():
    TelemetryService._instance = None

@pytest.fixture
def telemetry_service(tmp_path):
    # Set env vars
    os.environ['GREEN_AI_TELEMETRY'] = 'true'
    os.environ['GREEN_AI_ANONYMIZE'] = 'true'

    reset_telemetry_service()
    service = TelemetryService()
    # Override storage path to temp dir
    service.storage_path = tmp_path / 'telemetry.jsonl'

    yield service

    # Cleanup
    reset_telemetry_service()
    if 'GREEN_AI_TELEMETRY' in os.environ:
        del os.environ['GREEN_AI_TELEMETRY']

def test_telemetry_initialization(telemetry_service):
    assert telemetry_service.enabled is True
    assert telemetry_service.anonymize is True
    assert isinstance(telemetry_service.events, list)

def test_anonymize_logic(telemetry_service):
    project_id = "my-secret-project"
    anonymized = telemetry_service._anonymize(project_id)
    assert anonymized != project_id
    assert len(anonymized) == 64 # SHA256 hex digest length
    # Deterministic
    assert anonymized == telemetry_service._anonymize(project_id)

def test_track_scan_persistence(telemetry_service):
    violations = [{'id': 'rule1', 'severity': 'high'}]
    telemetry_service.track_scan(
        project_id="test-project",
        duration=1.5,
        language="python",
        violations=violations,
        codebase_emissions=0.1,
        scanning_emissions=0.01
    )

    # Check in-memory
    assert len(telemetry_service.events) == 1
    event = telemetry_service.events[0]
    assert event.event_type == 'scan_complete'

    # Check file persistence
    assert telemetry_service.storage_path.exists()
    with open(telemetry_service.storage_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 1
        saved_event = json.loads(lines[0])
        assert saved_event['event_type'] == 'scan_complete'
        assert saved_event['payload']['project_id'] != "test-project" # Anonymized
        assert len(saved_event['payload']['project_id']) == 64

def test_telemetry_disabled():
    os.environ['GREEN_AI_TELEMETRY'] = 'false'
    reset_telemetry_service()
    service = TelemetryService()
    assert service.enabled is False

    service.track_error('test', 'message')
    assert len(service.events) == 0

def test_track_error(telemetry_service):
    telemetry_service.track_error('validation_error', 'Invalid input')
    assert len(telemetry_service.events) == 1
    assert telemetry_service.events[0].event_type == 'error'

    with open(telemetry_service.storage_path, 'r') as f:
        saved_event = json.loads(f.read())
        assert saved_event['payload']['type'] == 'validation_error'
