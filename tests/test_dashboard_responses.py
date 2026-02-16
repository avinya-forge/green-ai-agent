"""
Tests for Dashboard API Responses and Error Handling
"""

import pytest
from unittest.mock import patch

# client fixture is in conftest.py

class TestDashboardResponses:
    """Test dashboard API responses for correctness"""

    def test_api_charts_content_type(self, client):
        """Test that api_charts returns application/json"""
        with patch('src.ui.state.last_charts', {'data': [1, 2, 3]}):
            response = client.get('/api/charts')
            assert 'application/json' in response.headers['content-type']

    def test_api_results_content_type(self, client):
        """Test that api_results returns application/json"""
        with patch('src.ui.state.last_scan_results', {'issues': []}):
            response = client.get('/api/results')
            assert 'application/json' in response.headers['content-type']
