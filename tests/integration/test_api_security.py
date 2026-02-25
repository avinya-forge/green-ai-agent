import pytest
from fastapi.testclient import TestClient
from src.ui.app_fastapi import app
import time

@pytest.fixture
def client():
    return TestClient(app)

def test_security_headers(client):
    """Verify security headers are present in responses."""
    response = client.get("/")
    # Even if 200 or 429, headers should be there.
    # If rate limit is already hit from other tests, status might be 429.

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

def test_rate_limiting_enforcement(client):
    """Verify rate limiting blocks excessive requests."""
    # We need a unique IP to avoid conflict with other tests if running in parallel (unlikely here)
    # TestClient allows setting client info

    # Create a client with a unique IP
    client_ip = "192.168.1.100"
    headers = {"X-Forwarded-For": client_ip}
    # Note: Starlette TestClient uses client host from scope.
    # standard TestClient doesn't easily let us change client host per request unless we construct it.

    # However, TestClient(app, base_url="http://testserver", client=("192.168.1.100", 1234))
    custom_client = TestClient(app, client=("192.168.1.100", 12345))

    limit = 100
    for i in range(limit):
        response = custom_client.get("/")
        assert response.status_code == 200, f"Request {i+1} failed with {response.status_code}"

    # The 101th request should fail
    response = custom_client.get("/")
    assert response.status_code == 429
    assert response.json()["detail"] == "Too Many Requests"
    assert "Retry-After" in response.headers

def test_security_headers_on_rate_limit(client):
    """Verify security headers are present even on 429 responses."""
    # Use another unique IP
    custom_client = TestClient(app, client=("192.168.1.101", 12345))

    # Exhaust limit
    for _ in range(100):
        custom_client.get("/")

    # Trigger 429
    response = custom_client.get("/")
    assert response.status_code == 429

    # Check headers
    # Debugging
    print(f"DEBUG Headers: {dict(response.headers)}")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
