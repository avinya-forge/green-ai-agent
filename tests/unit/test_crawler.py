from src.core.news.crawler import NewsCrawler

def test_news_crawler_init():
    crawler = NewsCrawler()
    assert len(crawler.sources) > 0


class MockResponse:
    def __init__(self, json_data, status=200):
        self.json_data = json_data
        self.status = status

    def read(self):
        import json
        return json.dumps(self.json_data).encode('utf-8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_fetch_top_stories_mock(monkeypatch):
    import urllib.request

    def mock_urlopen(req, timeout=10):
        url = req.full_url
        if "topstories" in url:
            return MockResponse([1, 2, 3])
        elif "item/1.json" in url:
            return MockResponse(
                {"id": 1, "title": "Test Story 1", "url": "http://test1.com"})
        elif "item/2.json" in url:
            return MockResponse(
                {"id": 2, "title": "Test Story 2", "url": "http://test2.com"})
        return MockResponse({})

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    crawler = NewsCrawler()
    stories = crawler.fetch_top_stories(limit=2)

    assert len(stories) == 2
    assert stories[0]["title"] == "Test Story 1"
    assert stories[1]["title"] == "Test Story 2"


def test_fetch_top_stories_error(monkeypatch):
    import urllib.request

    def mock_urlopen(req, timeout=10):
        raise Exception("Network error")

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    crawler = NewsCrawler()
    stories = crawler.fetch_top_stories()

    # Should handle error gracefully and return empty list
    assert stories == []

def test_fetch_hn_story_error(monkeypatch):
    import urllib.request

    def mock_urlopen(req, timeout=10):
        raise Exception("Network error")

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    crawler = NewsCrawler()
    story = crawler.fetch_hn_story(999)
    assert story == {}
