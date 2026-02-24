import os
import json
import hashlib
import time
import shutil
import tempfile
from typing import List, Dict, Optional, Tuple

from src.utils.logger import logger
try:
    from src.version import __version__
except ImportError:
    __version__ = "0.0.0"

class DiskCache:
    """
    Disk-based cache for scan results.
    Stores violations as JSON files keyed by content hash + language + version.
    """

    def __init__(self, cache_dir: str = ".green-ai/cache"):
        self.cache_dir = os.path.expanduser(cache_dir)
        self.version = __version__
        self._cache_dir_created = False

    def _ensure_cache_dir(self):
        """Ensure cache directory exists."""
        if self._cache_dir_created:
            return
        os.makedirs(self.cache_dir, exist_ok=True)
        self._cache_dir_created = True

    def _get_hash(self, content: str, language: str) -> str:
        """Compute MD5 hash of content and language + version."""
        hasher = hashlib.md5()
        hasher.update(content.encode('utf-8'))
        hasher.update(language.encode('utf-8'))
        hasher.update(self.version.encode('utf-8'))
        return hasher.hexdigest()

    def _get_path(self, key: str) -> str:
        """Get file path for a cache key (nested structure)."""
        subdir = os.path.join(self.cache_dir, key[:2])
        if not os.path.isdir(subdir):
            os.makedirs(subdir, exist_ok=True)
        return os.path.join(subdir, f"{key}.json")

    def get(self, content: str, language: str) -> Optional[List[Dict]]:
        """
        Retrieve cached violations.
        Returns None if not found or error reading.
        """
        key = self._get_hash(content, language)
        path = self._get_path(key)

        if not os.path.exists(path):
            return None

        try:
            # Update access time
            os.utime(path, None)

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Verify version (redundant due to hash inclusion but good for debugging)
                if data.get('version') != self.version:
                    return None
                return data.get('violations')
        except Exception as e:
            logger.debug(f"Cache read error for {path}: {e}")
            return None

    def set(self, content: str, language: str, violations: List[Dict]) -> None:
        """
        Store violations in cache using atomic write.
        """
        self._ensure_cache_dir()
        key = self._get_hash(content, language)
        path = self._get_path(key)

        data = {
            'violations': violations,
            'timestamp': time.time(),
            'version': self.version
        }

        try:
            # Atomic write: write to temp file then rename
            # Use same directory as target file to ensure atomic rename
            target_dir = os.path.dirname(path)
            fd, temp_path = tempfile.mkstemp(dir=target_dir, text=True)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f)

            os.replace(temp_path, path)
        except Exception as e:
            logger.warning(f"Failed to write cache for {path}: {e}")
            # Clean up temp file if rename failed
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def clear(self) -> None:
        """Clear all cache files."""
        if not os.path.exists(self.cache_dir):
            return

        try:
            shutil.rmtree(self.cache_dir)
            self._cache_dir_created = False
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")

    def prune(self, ttl_seconds: int = 86400) -> int:
        """
        Remove cache files older than TTL (based on modification time).
        Returns number of files removed.
        """
        if not os.path.exists(self.cache_dir):
            return 0

        count = 0
        now = time.time()

        try:
            for root, dirs, files in os.walk(self.cache_dir):
                for filename in files:
                    if not filename.endswith('.json'):
                        continue

                    path = os.path.join(root, filename)
                    try:
                        mtime = os.path.getmtime(path)
                        if now - mtime > ttl_seconds:
                            os.remove(path)
                            count += 1
                    except OSError:
                        continue

            # Remove empty directories
            for root, dirs, files in os.walk(self.cache_dir, topdown=False):
                if not os.listdir(root):
                    try:
                        os.rmdir(root)
                    except OSError:
                        pass

        except Exception as e:
            logger.warning(f"Error during cache pruning: {e}")

        return count
