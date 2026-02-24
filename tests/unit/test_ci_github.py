import pytest
from unittest.mock import patch, MagicMock
from src.core.ci.github_client import GitHubClient
import os

class TestGitHubClient:

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_init_with_env_var(self):
        client = GitHubClient()
        assert client.token == "test_token"

    def test_init_without_token(self):
        # Ensure GITHUB_TOKEN is not in env
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                GitHubClient()

    @patch("httpx.Client")
    def test_post_comment(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123, "body": "test comment"}
        mock_client.post.return_value = mock_response

        client = GitHubClient(token="test_token")
        result = client.post_comment("owner", "repo", 1, "test comment")

        assert result["id"] == 123
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args
        assert args[0] == "https://api.github.com/repos/owner/repo/issues/1/comments"
        assert kwargs["json"] == {"body": "test comment"}
        assert "Authorization" in kwargs["headers"]

    @patch("httpx.Client")
    def test_get_pr_diff(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "diff content"
        mock_client.get.return_value = mock_response

        client = GitHubClient(token="test_token")
        diff = client.get_pr_diff("owner", "repo", 1)

        assert diff == "diff content"
        mock_client.get.assert_called_once()
        args, kwargs = mock_client.get.call_args
        assert args[0] == "https://api.github.com/repos/owner/repo/pulls/1"
        assert kwargs["headers"]["Accept"] == "application/vnd.github.v3.diff"
