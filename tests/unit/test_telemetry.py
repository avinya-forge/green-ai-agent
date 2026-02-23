import pytest
from src.core.telemetry.service import TelemetryService
from src.core.telemetry.schemas import ScanMetrics

def test_telemetry_service_singleton():
    s1 = TelemetryService()
    s2 = TelemetryService()
    assert s1 is s2

def test_track_scan():
    service = TelemetryService()
    # Reset events for test
    service.events = []

    violations = [
        {'id': 'rule1', 'severity': 'high'},
        {'id': 'rule2', 'severity': 'low'}
    ]

    service.track_scan(
        project_id="test_project",
        duration=1.5,
        language="python",
        violations=violations,
        codebase_emissions=0.5,
        scanning_emissions=0.1
    )

    assert len(service.events) == 1
    event = service.events[0]
    assert event.event_type == 'scan_complete'

    payload = event.payload
    assert payload['project_id'] == 'test_project'
    assert payload['total_violations'] == 2
    assert payload['violations_by_severity']['high'] == 1
    assert payload['violations_by_severity']['low'] == 1

def test_export_events(tmp_path):
    service = TelemetryService()
    service.events = []
    service.track_error('test_error', 'something happened')

    output_file = tmp_path / "telemetry.json"
    service.export_events(str(output_file))

    assert output_file.exists()
    import json
    with open(output_file) as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]['event_type'] == 'error'
