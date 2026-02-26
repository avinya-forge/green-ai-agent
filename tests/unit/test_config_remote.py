import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
from pathlib import Path
from src.core.config import ConfigLoader

class TestConfigRemote(unittest.TestCase):
    def setUp(self):
        self.cache_dir = Path.home() / '.green-ai' / 'remote_configs'
        # Clean up before test if it exists to ensure clean state
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)

    def tearDown(self):
        # Clean up after test
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)

    @patch('src.core.config.httpx')
    def test_fetch_remote_config(self, mock_httpx):
        """Test fetching remote config and caching it."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "languages: [python]"
        mock_httpx.get.return_value = mock_response

        loader = ConfigLoader()
        url = "https://example.com/config.yaml"

        # Test fetching
        # We access the private method to test it directly
        config_path = loader._fetch_remote_config(url)

        # Verify httpx called
        mock_httpx.get.assert_called_with(url, timeout=10.0, follow_redirects=True)

        # Verify file cached
        self.assertTrue(os.path.exists(config_path))
        with open(config_path, 'r') as f:
            content = f.read()
            self.assertEqual(content, "languages: [python]")

    @patch('src.core.config.httpx')
    def test_fetch_remote_config_cached(self, mock_httpx):
        """Test that subsequent calls use the cache."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "languages: [python]"
        mock_httpx.get.return_value = mock_response

        loader = ConfigLoader()
        url = "https://example.com/config.yaml"

        # First fetch
        path1 = loader._fetch_remote_config(url)

        # Reset mock to verify it's NOT called second time
        mock_httpx.get.reset_mock()

        # Second fetch
        path2 = loader._fetch_remote_config(url)

        self.assertEqual(path1, path2)
        mock_httpx.get.assert_not_called()

    @patch('src.core.config.httpx')
    def test_load_from_url(self, mock_httpx):
        """Test loading config directly from a URL via constructor."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        # YAML content
        mock_response.text = "languages:\n  - go"
        mock_httpx.get.return_value = mock_response

        url = "https://example.com/config.yaml"
        loader = ConfigLoader(config_path=url)

        config = loader.load()

        self.assertEqual(config['languages'], ['go'])

if __name__ == '__main__':
    unittest.main()
