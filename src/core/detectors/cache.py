import hashlib
from typing import List, Dict, Optional, Tuple
from collections import OrderedDict

class DetectionCache:
    """
    In-memory LRU cache for detection results using OrderedDict.
    Keys are (content_hash, language).
    Values are list of violations.
    """

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        # OrderedDict maintains insertion order.
        # We will keep MRU at the end, LRU at the beginning.
        self.cache: OrderedDict[Tuple[str, str], List[Dict]] = OrderedDict()

    def get(self, content: str, language: str) -> Optional[List[Dict]]:
        """Get violations from cache if exists."""
        key = self._make_key(content, language)
        if key in self.cache:
            # Move to end (mark as recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def set(self, content: str, language: str, violations: List[Dict]) -> None:
        """Set violations in cache."""
        key = self._make_key(content, language)
        if key in self.cache:
            # Move to end if it exists (update)
            self.cache.move_to_end(key)

        self.cache[key] = violations

        if len(self.cache) > self.capacity:
            # Pop the first item (LRU)
            self.cache.popitem(last=False)

    def _make_key(self, content: str, language: str) -> Tuple[str, str]:
        """Create a hash key for the content."""
        # MD5 is fast enough for this purpose
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        return (content_hash, language)

# Global instance
detection_cache = DetectionCache()
