import urllib.request
import json
from typing import List, Dict, Any


class NewsCrawler:
    """
    Crawls technology and security news sources to provide updates for the dashboard.
    """

    def __init__(self, sources: List[str] = None):
        self.sources = sources or [
            "https://hacker-news.firebaseio.com/v0/topstories.json"
        ]

    def fetch_top_stories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetches top stories from configured sources."""
        stories = []
        for source in self.sources:
            try:
                # We use urllib to avoid adding third party deps like requests if not necessary
                req = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        # If it's HN style list of IDs
                        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], int):
                            for story_id in data[:limit]:
                                story = self.fetch_hn_story(story_id)
                                if story:
                                    stories.append(story)
            except Exception as e:
                print(f"Error fetching from {source}: {e}")
        return stories

    def fetch_hn_story(self, story_id: int) -> Dict[str, Any]:
        """Fetches a specific Hacker News story by ID."""
        url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode())
        except Exception as e:
            print(f"Error fetching story {story_id}: {e}")
        return {}
