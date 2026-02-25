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

    def parse_diff(self, diff_text: str) -> Dict[str, set]:
        """
        Parse a git diff string and return a dictionary mapping
        filenames to a set of changed line numbers in the new file.
        """
        changes = {}
        current_file = None
        current_line_new = 0

        for line in diff_text.splitlines():
            if line.startswith('+++ b/'):
                current_file = line[6:].strip()
                changes[current_file] = set()
            elif line.startswith('@@'):
                # Chunk header: @@ -old_start,old_len +new_start,new_len @@
                if current_file:
                    try:
                        # Extract new_start
                        parts = line.split()
                        # parts[2] is +new_start,new_len
                        new_info = parts[2]
                        if ',' in new_info:
                            start_str = new_info.split(',')[0]
                        else:
                            start_str = new_info

                        # Remove '+' prefix
                        current_line_new = int(start_str[1:])
                    except (ValueError, IndexError):
                        pass
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line
                if current_file:
                    changes[current_file].add(current_line_new)
                    current_line_new += 1
            elif line.startswith(' '):
                # Context line
                current_line_new += 1
            # '-' lines are removed, don't affect new line numbers

        return changes
