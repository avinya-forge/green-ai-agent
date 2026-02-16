import pytest
import json
from unittest.mock import patch

# client fixture is in conftest.py

class TestJsonResponsesVerification:
    """Explicit verification for api_charts and api_results"""

    def test_api_charts_with_data(self, client):
        """Verify api_charts returns correct JSON structure and content type"""
        mock_charts = {'severity_chart': {'data': [1, 2, 3]}}
        with patch('src.ui.state.last_charts', mock_charts):
            response = client.get('/api/charts')
            assert response.status_code == 200
            assert 'application/json' in response.headers['content-type']
            assert response.json() == mock_charts

    def test_api_charts_empty(self, client):
        """Verify api_charts returns empty JSON object when no data"""
        with patch('src.ui.state.last_charts', None):
            response = client.get('/api/charts')
            assert response.status_code == 200
            assert 'application/json' in response.headers['content-type']
            assert response.json() == {}

    def test_api_results_with_data(self, client):
        """Verify api_results returns correct JSON structure and content type"""
        mock_results = {'issues': [{'id': 'test', 'severity': 'high'}], 'emissions': 0.5}
        with patch('src.ui.state.last_scan_results', mock_results):
            response = client.get('/api/results')
            assert response.status_code == 200
            assert 'application/json' in response.headers['content-type']
            assert response.json() == mock_results

    def test_api_results_empty(self, client):
        """Verify api_results returns empty JSON object when no data"""
        with patch('src.ui.state.last_scan_results', None):
            response = client.get('/api/results')
            assert response.status_code == 200
            assert 'application/json' in response.headers['content-type']
            assert response.json() == {}
