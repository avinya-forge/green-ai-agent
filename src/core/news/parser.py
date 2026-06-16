from typing import List, Dict, Any
from src.core.news.crawler import NewsCrawler


class NewsParser:
    """
    Parses and normalizes news articles crawled from various sources
    into a standardized internal format for the dashboard.
    """

    def __init__(self, crawler: NewsCrawler = None):
        self.crawler = crawler or NewsCrawler()

    def normalize_article(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes a raw article dictionary into standard schema:
        { "id", "title", "url", "source", "timestamp", "score" }
        """
        if not raw_data:
            return {}

        # HackerNews normalization
        return {
            "id": str(raw_data.get("id", "")),
            "title": raw_data.get("title", "Untitled"),
            "url": raw_data.get("url", ""),
            "source": "HackerNews",
            "timestamp": raw_data.get("time", 0),
            "score": raw_data.get("score", 0),
        }

    def get_latest_news(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches, parses and normalizes the latest news.
        """
        raw_stories = self.crawler.fetch_top_stories(limit=limit)
        normalized = []
        for story in raw_stories:
            norm = self.normalize_article(story)
            if norm and norm.get("id"):
                normalized.append(norm)
        return normalized
