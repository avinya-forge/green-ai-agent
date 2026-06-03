import pytest
from fastapi.testclient import TestClient
from src.ui.app_fastapi import app
import os

client = TestClient(app)

def test_api_remediation_preview_path_traversal():
    """Verify that /api/remediation/preview is protected against path traversal."""
    # Attempt to access a file outside the project root
    traversal_path = "../../../../../etc/passwd"

    response = client.get(
        "/api/remediation/preview",
        params={
            "project": "test",
            "file": traversal_path,
            "line": 1,
            "issue_id": "test_rule"
        }
    )

    # It should either be a 400 Bad Request or 404 (if it doesn't resolve to a real file on the system)
    # The current implementation raises 400 "File path outside project root"
    assert response.status_code == 400
    assert "outside project root" in response.json()['detail']

def test_api_remediation_preview_valid_path():
    """Verify that /api/remediation/preview works for valid paths within root."""
    # Use a file that is known to exist within the project
    valid_path = "src/ui/app_fastapi.py"

    response = client.get(
        "/api/remediation/preview",
        params={
            "project": "Green-AI Agent",
            "file": valid_path,
            "line": 1,
            "issue_id": "unused_variable" # Just an example
        }
    )

    # 200 OK because it is inside the project root
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

def test_api_remediation_preview_nonexistent_file():
    """Verify that /api/remediation/preview returns 404 for nonexistent files within root."""
    nonexistent_path = "src/nonexistent_file_xyz.py"

    response = client.get(
        "/api/remediation/preview",
        params={
            "project": "test",
            "file": nonexistent_path,
            "line": 1,
            "issue_id": "test_rule"
        }
    )

    assert response.status_code == 404
    assert "File not found" in response.json()['detail']
