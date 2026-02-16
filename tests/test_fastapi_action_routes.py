from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, ANY
from src.ui.app_fastapi import app
import src.ui.state as state

client = TestClient(app)

def test_api_scan():
    # We need to mock asyncio.get_running_loop because TestClient runs in sync context
    # but the endpoint calls get_running_loop.
    # Actually, TestClient uses Starlette which runs app in a thread or loop.
    # But get_running_loop might fail if called from sync code not in a loop.
    # However, FastAPI endpoints defined with async def run in the loop.

    with patch('src.ui.state.get_project_manager') as mock_pm_get, \
         patch('threading.Thread') as mock_thread, \
         patch('asyncio.get_running_loop') as mock_loop:

         # Setup mock PM
         mock_pm = MagicMock()
         mock_pm.get_project.return_value = None # New project
         mock_pm_get.return_value = mock_pm

         response = client.post("/api/scan", json={
             "project_name": "TestProject",
             "language": "python",
             "path": "/tmp/test"
         })

         assert response.status_code == 200
         mock_pm.add_project.assert_called()
         mock_thread.assert_called()
         mock_thread.return_value.start.assert_called()

def test_delete_project():
    mock_pm = MagicMock()
    mock_project = MagicMock()
    mock_project.is_system = False
    mock_pm.get_project.return_value = mock_project

    with patch('src.ui.state.get_project_manager', return_value=mock_pm):
        response = client.delete("/api/projects/TestProject")
        assert response.status_code == 200
        mock_pm.remove_project.assert_called_with("TestProject")

def test_enable_standard():
    mock_registry = MagicMock()
    with patch('src.ui.state.get_standards_registry', return_value=mock_registry):
        response = client.post("/api/standards/green-software/enable")
        assert response.status_code == 200
        mock_registry.enable_standard.assert_called_with("green-software")

def test_export_csv():
    # Mock last_scan_results
    with patch('src.ui.state.last_scan_results', {'issues': []}), \
         patch('src.core.export.CSVExporter') as MockExporter, \
         patch('builtins.open', new_callable=MagicMock) as mock_open, \
         patch('pathlib.Path.mkdir'), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.unlink'):

         mock_file = MagicMock()
         mock_file.read.return_value = "csv_content"
         mock_open.return_value.__enter__.return_value = mock_file

         response = client.get("/api/export/csv")
         assert response.status_code == 200
         assert response.text == "csv_content"
         # Content type matching might be case sensitive or include charset
         assert "text/csv" in response.headers["content-type"]
