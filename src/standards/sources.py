"""
Standard Sources Module
Handles fetching and parsing of green software standards from remote sources.
"""

import requests
import yaml
import json
from typing import List, Dict
from abc import ABC, abstractmethod
from .registry import StandardRule


class StandardSource(ABC):
    """Abstract base class for standard sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the standard source."""

    @abstractmethod
    def fetch(self) -> List[StandardRule]:
        """Fetch rules from the source."""


class GitHubStandardSource(StandardSource):
    """Base class for standards hosted on GitHub."""

    def __init__(self, owner: str, repo: str, path: str, branch: str = "main"):
        self.owner = owner
        self.repo = repo
        self.path = path
        self.branch = branch

    def _get_raw_url(self) -> str:
        return f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{self.path}"

    def fetch_content(self) -> str:
        url = self._get_raw_url()
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching from {url}: {e}")
            return ""


class GSFSource(GitHubStandardSource):
    """Fetcher for Green Software Foundation standards."""

    @property
    def name(self) -> str:
        return "gsf"

    def __init__(self):
        # Hypothetical path, in reality we might need to parse the repo structure
        super().__init__("Green-Software-Foundation", "standards", "standards.yaml")

    def fetch(self) -> List[StandardRule]:
        content = self.fetch_content()
        if not content:
            return []

        try:
            # Assuming YAML structure
            data = yaml.safe_load(content)
            rules = []
            if isinstance(data, list):
                for item in data:
                    # Map external format to StandardRule
                    rules.append(StandardRule(
                        id=item.get('id', 'unknown'),
                        name=item.get('title', 'Unknown Rule'),
                        description=item.get('description', ''),
                        severity=item.get('severity', 'major'),
                        languages=item.get('languages', []),
                        pattern=item.get('pattern', ''),
                        remediation=item.get('remediation', ''),
                        source='GSF'
                    ))
            return rules
        except yaml.YAMLError:
            return []


class EcoCodeSource(GitHubStandardSource):
    """Fetcher for ecoCode standards."""

    @property
    def name(self) -> str:
        return "ecocode"

    def __init__(self):
        super().__init__("green-code-initiative", "ecocode", "rules/python.json")

    def fetch(self) -> List[StandardRule]:
        content = self.fetch_content()
        if not content:
            return []

        try:
            data = json.loads(content)
            rules = []
            # Assuming ecoCode JSON structure
            if isinstance(data, dict) and 'rules' in data:
                for r in data['rules']:
                    rules.append(StandardRule(
                        id=r.get('id', ''),
                        name=r.get('name', ''),
                        description=r.get('summary', ''),
                        severity=r.get('severity', 'minor'),
                        languages=['python'],  # specialized for python file
                        pattern=r.get('pattern', ''),
                        remediation=r.get('fix', ''),
                        source='ecoCode'
                    ))
            return rules
        except json.JSONDecodeError:
            return []


class SourceManager:
    """Manages multiple sources."""

    def __init__(self):
        self.sources: Dict[str, StandardSource] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.sources['gsf'] = GSFSource()
        self.sources['ecocode'] = EcoCodeSource()

    def fetch_all(self) -> Dict[str, List[StandardRule]]:
        results = {}
        for name, source in self.sources.items():
            try:
                rules = source.fetch()
                if rules:
                    results[name] = rules
            except Exception as e:
                print(f"Failed to sync source {name}: {e}")
        return results
