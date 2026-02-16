from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, PropertyMock
from src.ui.app_fastapi import app
import src.ui.state as state
from src.core.domain import ViolationDetails

client = TestClient(app)

def test_api_charts():
    with patch('src.ui.state.last_charts', {'data': [1, 2, 3]}):
        response = client.get("/api/charts")
        assert response.status_code == 200
        assert response.json() == {'data': [1, 2, 3]}

def test_api_results():
    with patch('src.ui.state.last_scan_results', {'issues': []}):
        response = client.get("/api/results")
        assert response.status_code == 200
        assert response.json() == {'issues': []}

def test_api_standards():
    mock_registry = MagicMock()
    mock_registry.list_standards.return_value = ["std1", "std2"]
    with patch('src.ui.state.get_standards_registry', return_value=mock_registry):
        response = client.get("/api/standards")
        assert response.status_code == 200
        assert response.json() == ["std1", "std2"]

def test_api_projects_list():
    mock_pm = MagicMock()
    mock_project = MagicMock()

    # Attributes
    mock_project.id = "proj-123"
    mock_project.name = "TestProject"
    mock_project.language = "python"
    mock_project.repo_url = "http://example.com"
    mock_project.branch = "main"
    mock_project.last_scan = None
    mock_project.latest_violations = 0
    mock_project.total_emissions = 0.0

    # Methods
    mock_project.get_grade.return_value = "A"

    # Properties - need to attach to the type of the mock or use a configured mock
    # A simpler way is to just set them as attributes if we are not testing logic that relies on them being properties
    # But ProjectSummaryDTO access them as attributes, so setting them on the instance works for MagicMock
    # UNLESS they are defined as properties in the class we are mocking?
    # Here we are mocking the whole object, so setting attributes is enough.
    # However, MagicMock by default creates a new MagicMock when accessing an attribute.
    # We need to set them to values.

    mock_project.high_violations = 0
    mock_project.medium_violations = 0
    mock_project.low_violations = 0

    mock_pm.list_projects.return_value = [mock_project]

    with patch('src.ui.state.get_project_manager', return_value=mock_pm):
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert len(data['projects']) == 1
        assert data['projects'][0]['name'] == "TestProject"
        assert data['projects'][0]['id'] == "proj-123"

def test_landing_page():
    # Test that landing page renders
    mock_pm = MagicMock()
    mock_pm.list_projects.return_value = []
    with patch('src.ui.state.last_scan_results', None), \
         patch('src.ui.state.get_project_manager', return_value=mock_pm):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
