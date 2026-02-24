import os
import time
import tempfile
import shutil
import unittest
from src.core.cache import DiskCache

class TestDiskCache(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cache = DiskCache(cache_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_set_and_get(self):
        content = "print('hello')"
        language = "python"
        violations = [{"id": "test_violation", "message": "Test"}]

        self.cache.set(content, language, violations)

        # Verify file exists
        key = self.cache._get_hash(content, language)
        path = self.cache._get_path(key)
        self.assertTrue(os.path.exists(path))

        # Verify get
        cached = self.cache.get(content, language)
        self.assertEqual(cached, violations)

    def test_get_miss(self):
        content = "print('unknown')"
        language = "python"
        cached = self.cache.get(content, language)
        self.assertIsNone(cached)

    def test_clear(self):
        content = "print('hello')"
        language = "python"
        violations = []
        self.cache.set(content, language, violations)

        self.cache.clear()

        # Verify directory is gone
        self.assertFalse(os.path.exists(self.test_dir))

        # Verify get returns None
        cached = self.cache.get(content, language)
        self.assertIsNone(cached)

        # Verify set works again (recreates dir)
        self.cache.set(content, language, violations)
        self.assertTrue(os.path.exists(self.test_dir))

    def test_prune(self):
        content = "print('old')"
        language = "python"
        violations = []
        self.cache.set(content, language, violations)

        # Manually backdate the file
        key = self.cache._get_hash(content, language)
        path = self.cache._get_path(key)

        # Set mtime to 2 days ago
        old_time = time.time() - (2 * 86400)
        os.utime(path, (old_time, old_time))

        # Add new file
        content_new = "print('new')"
        self.cache.set(content_new, language, violations)

        # Prune older than 1 day
        removed = self.cache.prune(ttl_seconds=86400)

        self.assertEqual(removed, 1)
        self.assertIsNone(self.cache.get(content, language))
        self.assertIsNotNone(self.cache.get(content_new, language))
