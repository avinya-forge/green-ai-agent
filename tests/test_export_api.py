"""
Tests for Export API Endpoints
"""

import pytest
from unittest.mock import patch, MagicMock

# client fixture is now in conftest.py

class TestExportAPI:
    """Test export API endpoints"""

    def test_api_export_csv_no_results(self, client):
        """Test CSV export when no results are available"""
        with patch('src.ui.state.last_scan_results', None):
            response = client.get('/api/export/csv')
            assert response.status_code == 400
            assert 'No scan results available' in response.json()['detail']

    def test_api_export_html_no_results(self, client):
        """Test HTML export when no results are available"""
        with patch('src.ui.state.last_scan_results', None):
            response = client.get('/api/export/html')
            assert response.status_code == 400
            assert 'No scan results available' in response.json()['detail']

    def test_api_export_csv_success(self, client):
        """Test successful CSV export"""
        mock_results = {'issues': []}

        # We need to mock open because _handle_export reads the file back
        mock_open = MagicMock()
        mock_file = MagicMock()
        mock_file.read.return_value = "header1,header2\nval1,val2"
        mock_open.return_value.__enter__.return_value = mock_file

        # We need to mock Path object returned by OUTPUT_DIR / filename
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.name = 'green-ai-report-TestProject.csv'
        mock_path.__str__.return_value = '/tmp/green-ai-report-TestProject.csv'

        with patch('src.ui.state.last_scan_results', mock_results), \
             patch('src.core.export.CSVExporter') as MockExporter, \
             patch('builtins.open', mock_open), \
             patch('src.ui.app_fastapi.OUTPUT_DIR') as MockOutputDir:

            MockOutputDir.__truediv__.return_value = mock_path

            response = client.get('/api/export/csv?project=TestProject')

            assert response.status_code == 200
            assert 'text/csv' in response.headers['content-type']
            # Check filename in content disposition
            assert 'filename="green-ai-report-TestProject.csv"' in response.headers['Content-Disposition']

            # Verify mkdir called
            MockOutputDir.mkdir.assert_called_with(parents=True, exist_ok=True)
            # Verify cleanup
            mock_path.unlink.assert_called()

    def test_api_export_html_success(self, client):
        """Test successful HTML export"""
        mock_results = {'issues': []}

        mock_open = MagicMock()
        mock_file = MagicMock()
        mock_file.read.return_value = "<html>Content</html>"
        mock_open.return_value.__enter__.return_value = mock_file

        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.name = 'green-ai-report-TestProject.html'
        mock_path.__str__.return_value = '/tmp/green-ai-report-TestProject.html'

        with patch('src.ui.state.last_scan_results', mock_results), \
             patch('src.core.export.HTMLReporter') as MockReporter, \
             patch('builtins.open', mock_open), \
             patch('src.ui.app_fastapi.OUTPUT_DIR') as MockOutputDir:

            MockOutputDir.__truediv__.return_value = mock_path

            response = client.get('/api/export/html?project=TestProject')

            assert response.status_code == 200
            assert 'text/html' in response.headers['content-type']

            # Verify mkdir called
            MockOutputDir.mkdir.assert_called_with(parents=True, exist_ok=True)
            # Verify cleanup
            mock_path.unlink.assert_called()
