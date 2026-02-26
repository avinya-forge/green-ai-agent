import unittest
from src.core.detectors.cache import DetectionCache

class TestDetectionCache(unittest.TestCase):
    def test_lru_behavior(self):
        """Test that the cache correctly evicts the least recently used item."""
        cache = DetectionCache(capacity=2)

        # Add two items
        cache.set("content1", "python", [{"id": 1}])
        cache.set("content2", "python", [{"id": 2}])

        # Verify both are present
        self.assertEqual(cache.get("content1", "python"), [{"id": 1}])
        self.assertEqual(cache.get("content2", "python"), [{"id": 2}])

        # Access content1 to make it most recently used
        cache.get("content1", "python")

        # Add a third item, should evict content2 (LRU) because content1 was just accessed
        cache.set("content3", "python", [{"id": 3}])

        # content1 should still be there
        self.assertEqual(cache.get("content1", "python"), [{"id": 1}])
        # content2 should be gone
        self.assertIsNone(cache.get("content2", "python"))
        # content3 should be there
        self.assertEqual(cache.get("content3", "python"), [{"id": 3}])

    def test_update_existing(self):
        """Test that updating an existing item moves it to the MRU position."""
        cache = DetectionCache(capacity=2)
        cache.set("content1", "python", [{"id": 1}])
        cache.set("content2", "python", [{"id": 2}])

        # Update content1
        cache.set("content1", "python", [{"id": 1, "updated": True}])

        # Add content3. If content1 was correctly moved to MRU on update, content2 should be evicted.
        cache.set("content3", "python", [{"id": 3}])

        self.assertEqual(cache.get("content1", "python")[0]["updated"], True)
        self.assertIsNone(cache.get("content2", "python"))
        self.assertEqual(cache.get("content3", "python"), [{"id": 3}])

    def test_capacity_limit(self):
        """Test that capacity is strictly enforced."""
        cache = DetectionCache(capacity=1)
        cache.set("content1", "python", [{"id": 1}])
        self.assertIsNotNone(cache.get("content1", "python"))

        cache.set("content2", "python", [{"id": 2}])
        self.assertIsNone(cache.get("content1", "python"))
        self.assertIsNotNone(cache.get("content2", "python"))

if __name__ == '__main__':
    unittest.main()
