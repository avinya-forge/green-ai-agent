import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, ANY
from src.ui.app_fastapi import app
import src.ui.state as state

@pytest.mark.anyio
async def test_api_scan():
    # We don't mock asyncio.get_running_loop because we are running in the loop
    with patch('src.ui.state.get_project_manager') as mock_pm_get, \
         patch('threading.Thread') as mock_thread:

         # Setup mock PM
         mock_pm = MagicMock()
         mock_pm.get_project.return_value = None # New project
         mock_pm_get.return_value = mock_pm

         transport = ASGITransport(app=app)
         async with AsyncClient(transport=transport, base_url="http://test") as client:
             response = await client.post("/api/scan", json={
                 "project_name": "TestProject",
                 "language": "python",
                 "path": "/tmp/test"
             })

             assert response.status_code == 200
             mock_pm.add_project.assert_called()
             mock_thread.assert_called()
             mock_thread.return_value.start.assert_called()

@pytest.mark.anyio
async def test_delete_project():
    mock_pm = MagicMock()
    mock_project = MagicMock()
    mock_project.is_system = False
    mock_pm.get_project.return_value = mock_project

    with patch('src.ui.state.get_project_manager', return_value=mock_pm):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/api/projects/TestProject")
            assert response.status_code == 200
            mock_pm.remove_project.assert_called_with("TestProject")

@pytest.mark.anyio
async def test_enable_standard():
    mock_registry = MagicMock()
    with patch('src.ui.state.get_standards_registry', return_value=mock_registry):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/standards/green-software/enable")
            assert response.status_code == 200
            mock_registry.enable_standard.assert_called_with("green-software")

@pytest.mark.anyio
async def test_export_csv():
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

         transport = ASGITransport(app=app)
         async with AsyncClient(transport=transport, base_url="http://test") as client:
             response = await client.get("/api/export/csv")
             assert response.status_code == 200
             assert response.text == "csv_content"
             # Content type matching might be case sensitive or include charset
             assert "text/csv" in response.headers["content-type"]
