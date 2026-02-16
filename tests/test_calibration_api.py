import pytest
from unittest.mock import patch, MagicMock

# client fixture is in conftest.py

def test_get_calibration_profile(client):
    """Test that GET /api/calibrate returns the current profile."""
    # We mock CalibrationAgent to control the 'profile' attribute
    with patch('src.ui.app_fastapi.CalibrationAgent') as MockAgent:
        mock_agent_instance = MockAgent.return_value
        # Mock the profile property/attribute
        mock_agent_instance.profile = {
            'timestamp': 1234567890,
            'platform': 'TestPlatform',
            'coefficients': {'cpu_multiplier': 1.5, 'efficiency_tier': 'Standard'}
        }

        response = client.get('/api/calibrate')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert data['profile']['platform'] == 'TestPlatform'
        assert data['profile']['coefficients']['cpu_multiplier'] == 1.5

def test_post_calibration_run(client):
    """Test that POST /api/calibrate triggers calibration."""
    with patch('src.ui.app_fastapi.CalibrationAgent') as MockAgent:
        mock_agent_instance = MockAgent.return_value
        # Mock run_calibration to return a new profile
        new_profile = {
            'timestamp': 9876543210,
            'platform': 'NewTestPlatform',
            'coefficients': {'cpu_multiplier': 0.8, 'efficiency_tier': 'High'}
        }
        mock_agent_instance.run_calibration.return_value = new_profile

        response = client.post('/api/calibrate')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert data['profile'] == new_profile
        mock_agent_instance.run_calibration.assert_called_once()
