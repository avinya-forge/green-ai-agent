"""
OSV.dev API client for vulnerability lookups.
"""

import requests
from typing import List, Dict


class OSVClient:
    """
    Client for OSV (Open Source Vulnerabilities) database.
    """

    API_URL = "https://api.osv.dev/v1/query"

    def query_vulnerability(self, name: str, version: str, ecosystem: str = "PyPI") -> List[Dict]:
        """
        Query OSV for vulnerabilities in a specific package and version.
        """
        if version == 'unknown':
            return []

        query = {
            "version": version,
            "package": {
                "name": name,
                "ecosystem": ecosystem
            }
        }

        try:
            response = requests.post(self.API_URL, json=query, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('vulns', [])
        except Exception:
            pass
        return []

    def batch_query(self, dependencies: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Query vulnerabilities for a list of dependencies.
        """
        results = {}
        for dep in dependencies:
            ecosystem = "PyPI" if dep['type'] == 'python' else "npm"
            vulns = self.query_vulnerability(dep['name'], dep['version'], ecosystem)
            if vulns:
                results[dep['name']] = vulns
        return results
