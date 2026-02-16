"""
Tests for History API Endpoints
"""

import pytest
import json
from unittest.mock import patch, MagicMock


# client fixture is in conftest.py

class TestHistoryAPI:
    """Test history API endpoints"""
    
    def test_api_history_missing_project(self, client):
        """Test /api/history without project parameter"""
        response = client.get('/api/history')
        assert response.status_code == 422 # FastAPI validation error for missing query param
    
    def test_api_history_empty(self, client):
        """Test /api/history with no scans"""
        mock_hm = MagicMock()
        mock_hm.get_project_history.return_value = []

        with patch('src.ui.state.get_history_manager', return_value=mock_hm):
            response = client.get('/api/history?project=empty-project')
            assert response.status_code == 200
            data = response.json()
            assert data['project'] == 'empty-project'
            assert data['count'] == 0
            assert data['scans'] == []
    
    def test_api_trending_missing_project(self, client):
        """Test /api/trending without project parameter"""
        response = client.get('/api/trending')
        assert response.status_code == 422
    
    def test_api_trending_no_scans(self, client):
        """Test /api/trending with no history"""
        mock_hm = MagicMock()
        mock_hm.get_trending_data.return_value = {'trend': 'insufficient_data'}

        with patch('src.ui.state.get_history_manager', return_value=mock_hm):
            response = client.get('/api/trending?project=new-project')
            assert response.status_code == 200
            data = response.json()
            assert data['project'] == 'new-project'
            assert data['trend'] == 'insufficient_data'
    
    def test_api_compare_missing_project(self, client):
        """Test /api/compare without project parameter"""
        response = client.get('/api/compare')
        assert response.status_code == 422
    
    def test_api_compare_insufficient_scans(self, client):
        """Test /api/compare with fewer than 2 scans"""
        # We need to mock get_project_history to return 1 scan
        mock_hm = MagicMock()
        mock_hm.get_project_history.return_value = [MagicMock()]

        with patch('src.ui.state.get_history_manager', return_value=mock_hm):
            response = client.get('/api/compare?project=single-scan-project')
            assert response.status_code == 400
            data = response.json()
            assert 'Not enough scans' in data['detail']
    
    def test_api_history_invalid_project_name(self, client):
        """Test API with special characters in project name"""
        mock_hm = MagicMock()
        mock_hm.get_project_history.return_value = []

        with patch('src.ui.state.get_history_manager', return_value=mock_hm):
            response = client.get('/api/history?project=my%20project%20name')
            assert response.status_code == 200
            data = response.json()
            assert 'project' in data
            assert data['project'] == 'my project name' # decoded
    
    def test_api_endpoints_return_json(self, client):
        """Test that all history endpoints return valid JSON"""
        mock_hm = MagicMock()
        mock_hm.get_project_history.return_value = []
        mock_hm.get_trending_data.return_value = {'trend': 'insufficient_data'}

        with patch('src.ui.state.get_history_manager', return_value=mock_hm):
            # Test history endpoint
            response = client.get('/api/history?project=test')
            assert 'application/json' in response.headers['content-type']

            # Test trending endpoint
            response = client.get('/api/trending?project=test')
            assert 'application/json' in response.headers['content-type']

            # Test compare endpoint (will fail due to insufficient scans, but should return JSON)
            # Need to mock get_project_history to return < 2 scans
            # Default mock returns [], so it raises HTTPException 400
            response = client.get('/api/compare?project=test')
            assert 'application/json' in response.headers['content-type']
