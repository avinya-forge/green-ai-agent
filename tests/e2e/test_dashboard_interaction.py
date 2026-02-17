import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.ui.app_fastapi import app
from src.core.domain import Project, ViolationDetails

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_state():
    with patch('src.ui.app_fastapi.state') as mock_state:
        # Default mock setup
        mock_state.last_scan_results = {
            'issues': [],
            'scanning_emissions': 100.0,
            'codebase_emissions': 50.0,
            'total_emissions': 150.0,
            'summary': {'files': 10, 'lines': 500},
            'metadata': {'project_name': 'Test Project', 'language': 'python', 'path': '/tmp'},
            'project_name': 'Test Project' # Added for compatibility if needed
        }
        mock_state.last_charts = {'emissions': {}}

        # Mock Project Manager
        mock_pm = MagicMock()

        # Create a real Project instance for better fidelity
        real_project = Project(
            id="test-id",
            name="Test Project",
            repo_url="http://example.com",
            branch="main",
            language="python",
            last_scan="2023-10-27T10:00:00Z",
            scan_count=1,
            latest_violations=5,
            total_emissions=10.5,
            violation_details=ViolationDetails(critical=1, high=1, major=1, medium=1, minor=1)
        )

        mock_pm.list_projects.return_value = [real_project]
        mock_pm.get_project.return_value = real_project
        mock_state.get_project_manager.return_value = mock_pm

        # Mock History Manager
        mock_hm = MagicMock()
        mock_hm.get_project_history.return_value = []
        mock_state.get_history_manager.return_value = mock_hm

        # Mock Standards Registry
        mock_registry = MagicMock()
        mock_registry.list_standards.return_value = {'gsf': {'enabled': True}}
        mock_registry.standards = {'gsf': []}
        mock_state.get_standards_registry.return_value = mock_registry

        yield mock_state

def test_dashboard_landing_page(client, mock_state):
    """Test that the landing page loads successfully."""
    mock_state.last_scan_results = None  # Ensure we hit the landing page logic
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert b"Green-AI Agent" in response.content

def test_dashboard_with_results(client, mock_state):
    """Test the dashboard when scan results are present."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for emissions values rendered in the template
    # 100.000000000
    assert b"100.000000000" in response.content
    assert b"Violations Detected" in response.content

def test_api_projects_list(client, mock_state):
    """Test the projects API endpoint."""
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert len(data['projects']) == 1
    assert data['projects'][0]['name'] == "Test Project"
    assert data['projects'][0]['high_violations'] == 3 # 1 critical + 1 high + 1 major

def test_api_standards_list(client, mock_state):
    """Test the standards API endpoint."""
    response = client.get("/api/standards")
    assert response.status_code == 200
    data = response.json()
    assert 'gsf' in data

def test_api_export_csv(client, mock_state):
    """Test the CSV export endpoint."""
    with patch('src.ui.app_fastapi.CSVExporter') as MockExporter:
        mock_exporter_instance = MockExporter.return_value
        mock_exporter_instance.export.return_value = None

        # Mock open() to avoid file system interaction
        with patch('builtins.open', new_callable=MagicMock) as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = "csv,content"
            mock_open.return_value.__enter__.return_value = mock_file

            with patch('pathlib.Path.mkdir'):
                with patch('pathlib.Path.exists', return_value=True):
                     with patch('pathlib.Path.unlink') as mock_unlink:
                        response = client.get("/api/export/csv")

                        assert response.status_code == 200
                        assert response.headers["content-type"] == "text/csv; charset=utf-8"
                        assert response.content == b"csv,content"
                        MockExporter.assert_called_once()
                        mock_unlink.assert_called_once()

def test_api_scan_trigger(client, mock_state):
    """Test triggering a scan via API."""
    with patch('threading.Thread') as MockThread:
        payload = {
            "project_name": "New Project",
            "language": "python",
            "git_url": "https://github.com/example/repo.git"
        }
        response = client.post("/api/scan", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert data['project_name'] == "New Project"

        # Verify thread was started
        MockThread.assert_called_once()
        args, _ = MockThread.call_args
        assert MockThread.return_value.start.called

def test_api_calibrate(client):
    """Test the calibration endpoint."""
    with patch('src.ui.app_fastapi.CalibrationAgent') as MockAgent:
        mock_instance = MockAgent.return_value
        mock_instance.profile = {"cpu": "intel"}

        response = client.get("/api/calibrate")
        assert response.status_code == 200
        assert response.json() == {'status': 'ok', 'profile': {"cpu": "intel"}}
