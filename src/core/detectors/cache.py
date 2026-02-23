import hashlib
from typing import List, Dict, Optional, Tuple

class DetectionCache:
    """
    Simple in-memory LRU cache for detection results.
    Keys are (content_hash, language).
    Values are list of violations.
    """

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache: Dict[Tuple[str, str], List[Dict]] = {}
        self.order: List[Tuple[str, str]] = []

    def get(self, content: str, language: str) -> Optional[List[Dict]]:
        """Get violations from cache if exists."""
        key = self._make_key(content, language)
        if key in self.cache:
            # Move to end (most recently used)
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None

    def set(self, content: str, language: str, violations: List[Dict]) -> None:
        """Set violations in cache."""
        key = self._make_key(content, language)
        if key in self.cache:
            self.order.remove(key)

        self.cache[key] = violations
        self.order.append(key)

        if len(self.cache) > self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]

    def _make_key(self, content: str, language: str) -> Tuple[str, str]:
        """Create a hash key for the content."""
        # MD5 is fast enough for this purpose
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        return (content_hash, language)

# Global instance
detection_cache = DetectionCache()
