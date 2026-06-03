import pytest
from fastapi.testclient import TestClient
from src.ui.app_fastapi import app

def test_enhanced_security_headers():
    client = TestClient(app)
    response = client.get("/")
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "geolocation=()" in response.headers["Permissions-Policy"]
    assert "object-src 'none'" in response.headers["Content-Security-Policy"]
