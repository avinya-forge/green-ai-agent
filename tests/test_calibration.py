import pytest
import json
from unittest.mock import patch, MagicMock

# client fixture is in conftest.py

def test_api_calibrate_success(client):
    """Test that the calibration endpoint returns a valid profile."""
    # Mock CalibrationAgent.run_calibration to avoid running actual benchmarks
    mock_profile = {
        'platform': 'TestOS',
        'coefficients': {
            'cpu_multiplier': 1.5,
            'efficiency_tier': 'Standard'
        }
    }

    with patch('src.ui.app_fastapi.CalibrationAgent') as MockAgent:
        instance = MockAgent.return_value
        instance.run_calibration.return_value = mock_profile

        response = client.post('/api/calibrate')

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'ok'
        assert data['profile'] == mock_profile
        instance.run_calibration.assert_called_once()

def test_api_calibrate_failure(client):
    """Test error handling in calibration endpoint."""
    with patch('src.ui.app_fastapi.CalibrationAgent') as MockAgent:
        instance = MockAgent.return_value
        instance.run_calibration.side_effect = Exception("Benchmark failed")

        response = client.post('/api/calibrate')

        assert response.status_code == 500
        data = response.json()
        assert 'detail' in data
        assert data['detail'] == "Internal Server Error"
