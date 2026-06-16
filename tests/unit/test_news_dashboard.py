from fastapi.testclient import TestClient
from src.ui.app_fastapi import app

client = TestClient(app)


def test_api_news_dashboard(monkeypatch):
    import urllib.request
    from tests.unit.test_crawler import MockResponse

    def mock_urlopen(req, timeout=10):
        url = req.full_url
        if "topstories" in url:
            return MockResponse([1])
        elif "item/1.json" in url:
            return MockResponse({"id": 1, "title": "Test Story 1", "url": "http://test1.com"})
        return MockResponse({})

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    response = client.get("/api/news")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "articles" in data
