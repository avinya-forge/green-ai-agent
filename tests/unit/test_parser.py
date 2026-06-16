from src.core.news.parser import NewsParser


class MockCrawler:
    def fetch_top_stories(self, limit=5):
        return [
            {"id": 101, "title": "AI breakthroughs", "url": "http://ai.test", "time": 1600000000, "score": 150},
            {"id": 102, "title": "Security flaw found", "url": "http://sec.test", "time": 1600001000, "score": 200},
            {}  # Empty or malformed story
        ][:limit]


def test_normalize_article():
    parser = NewsParser()
    raw = {"id": 123, "title": "Test", "url": "http://test", "time": 1000, "score": 42}
    norm = parser.normalize_article(raw)

    assert norm["id"] == "123"
    assert norm["title"] == "Test"
    assert norm["url"] == "http://test"
    assert norm["source"] == "HackerNews"
    assert norm["timestamp"] == 1000
    assert norm["score"] == 42


def test_normalize_empty_article():
    parser = NewsParser()
    assert parser.normalize_article({}) == {}


def test_get_latest_news():
    parser = NewsParser(crawler=MockCrawler())
    news = parser.get_latest_news(limit=5)

    # Should only return 2 valid normalized articles (the 3rd was empty)
    assert len(news) == 2
    assert news[0]["id"] == "101"
    assert news[0]["title"] == "AI breakthroughs"
    assert news[1]["id"] == "102"
    assert news[1]["title"] == "Security flaw found"
