import os
import httpx
from typing import Optional, Dict, Any

class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required (set GITHUB_TOKEN env var or pass token)")

        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Green-AI-Scanner"
        }

    def post_comment(self, owner: str, repo: str, pr_number: int, body: str) -> Dict[str, Any]:
        """Post a comment to a Pull Request (via Issues API)."""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        payload = {"body": body}

        with httpx.Client() as client:
            response = client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Get the diff of a Pull Request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"

        with httpx.Client() as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
