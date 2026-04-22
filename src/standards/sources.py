"""
Standard Sources Module
Handles fetching and parsing of green software standards from remote sources.
Extended (EPIC-29) with OWASP Top 10, CWE/MITRE, and EPSS sources.
"""

import io
import json
import re
import requests
import yaml
import zipfile
from abc import ABC, abstractmethod
from typing import List, Dict

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
        return (
            f"https://raw.githubusercontent.com/{self.owner}/"
            f"{self.repo}/{self.branch}/{self.path}"
        )

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
        super().__init__("Green-Software-Foundation", "standards", "standards.yaml")

    def fetch(self) -> List[StandardRule]:
        content = self.fetch_content()
        if not content:
            return []

        try:
            data = yaml.safe_load(content)
            rules = []
            if isinstance(data, list):
                for item in data:
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
            if isinstance(data, dict) and 'rules' in data:
                for r in data['rules']:
                    rules.append(StandardRule(
                        id=r.get('id', ''),
                        name=r.get('name', ''),
                        description=r.get('summary', ''),
                        severity=r.get('severity', 'minor'),
                        languages=['python'],
                        pattern=r.get('pattern', ''),
                        remediation=r.get('fix', ''),
                        source='ecoCode'
                    ))
            return rules
        except json.JSONDecodeError:
            return []


class OWASPTop10Source(StandardSource):
    """
    Fetcher for OWASP Top 10 security risks.
    Fetches the OWASP Top 10 index page and extracts risk entries.
    Falls back to a curated embedded list when the remote is unavailable.
    """

    _URL = (
        "https://raw.githubusercontent.com/OWASP/"
        "www-project-top-ten/master/docs/index.md"
    )

    # Embedded fallback: OWASP Top 10 2021 (stable)
    _FALLBACK: List[dict] = [
        {"id": "A01:2021", "name": "Broken Access Control",
         "cwe": ["CWE-200", "CWE-201", "CWE-352"],
         "description": "Access control enforces policy so that users cannot act outside of their intended permissions."},
        {"id": "A02:2021", "name": "Cryptographic Failures",
         "cwe": ["CWE-259", "CWE-327", "CWE-331"],
         "description": "Failures related to cryptography which often lead to sensitive data exposure."},
        {"id": "A03:2021", "name": "Injection",
         "cwe": ["CWE-79", "CWE-89", "CWE-73"],
         "description": "SQL, NoSQL, OS, and LDAP injection, template injection, and prompt injection."},
        {"id": "A04:2021", "name": "Insecure Design",
         "cwe": ["CWE-209", "CWE-256", "CWE-501"],
         "description": "Missing or ineffective control design. Threat modeling and secure design principles needed."},
        {"id": "A05:2021", "name": "Security Misconfiguration",
         "cwe": ["CWE-16", "CWE-611"],
         "description": "Missing security hardening, unnecessary features enabled, default credentials in use."},
        {"id": "A06:2021", "name": "Vulnerable and Outdated Components",
         "cwe": ["CWE-1026", "CWE-1035", "CWE-1104"],
         "description": "Using components with known vulnerabilities without version management."},
        {"id": "A07:2021", "name": "Identification and Authentication Failures",
         "cwe": ["CWE-297", "CWE-287", "CWE-384"],
         "description": "Broken authentication — weak passwords, session fixation, credential stuffing."},
        {"id": "A08:2021", "name": "Software and Data Integrity Failures",
         "cwe": ["CWE-502", "CWE-829", "CWE-494"],
         "description": "Code and infrastructure that does not protect against integrity violations."},
        {"id": "A09:2021", "name": "Security Logging and Monitoring Failures",
         "cwe": ["CWE-117", "CWE-223", "CWE-778"],
         "description": "Insufficient logging, detection, monitoring, and active response."},
        {"id": "A10:2021", "name": "Server-Side Request Forgery",
         "cwe": ["CWE-918"],
         "description": "SSRF flaws occur when a web app fetches a remote resource without validating the URL."},
    ]

    @property
    def name(self) -> str:
        return "owasp"

    def fetch(self) -> List[StandardRule]:
        try:
            resp = requests.get(self._URL, timeout=10)
            resp.raise_for_status()
            entries = self._parse_markdown(resp.text)
        except requests.RequestException:
            entries = self._FALLBACK

        rules = []
        for entry in entries:
            rules.append(StandardRule(
                id=entry["id"].replace(":", "_").replace(" ", "_"),
                name=entry["name"],
                description=entry["description"],
                severity="critical",
                languages=["python", "javascript", "typescript", "java", "go", "csharp"],
                pattern="",
                remediation=f"Refer to OWASP Top 10 {entry['id']} guidance.",
                source="OWASP"
            ))
        return rules

    def _parse_markdown(self, text: str) -> List[dict]:
        """Extract A0x entries from OWASP markdown index."""
        entries = []
        pattern = re.compile(r"(A\d{2}:\d{4})[^\n]*?[-–]\s*([^\n]+)")
        for match in pattern.finditer(text):
            entries.append({
                "id": match.group(1),
                "name": match.group(2).strip(),
                "description": f"OWASP Top 10 risk: {match.group(2).strip()}",
                "cwe": [],
            })
        return entries if entries else self._FALLBACK


class CWESource(StandardSource):
    """
    Fetcher for CWE/MITRE Top 25 most dangerous software weaknesses.
    Uses MITRE's published JSON data feed.
    Falls back to embedded CWE Top 25 2024 when network unavailable.
    """

    _URL = "https://cwe.mitre.org/data/json/cwe_latest.json.zip"

    # Embedded fallback: CWE Top 25 2023 (stable public list)
    _FALLBACK: List[dict] = [
        {"id": "CWE-787", "name": "Out-of-bounds Write", "severity": "critical"},
        {"id": "CWE-79", "name": "Improper Neutralization of Input During Web Page Generation (XSS)", "severity": "critical"},
        {"id": "CWE-89", "name": "SQL Injection", "severity": "critical"},
        {"id": "CWE-416", "name": "Use After Free", "severity": "critical"},
        {"id": "CWE-78", "name": "OS Command Injection", "severity": "critical"},
        {"id": "CWE-20", "name": "Improper Input Validation", "severity": "major"},
        {"id": "CWE-125", "name": "Out-of-bounds Read", "severity": "major"},
        {"id": "CWE-22", "name": "Path Traversal", "severity": "critical"},
        {"id": "CWE-352", "name": "Cross-Site Request Forgery (CSRF)", "severity": "major"},
        {"id": "CWE-434", "name": "Unrestricted Upload of File with Dangerous Type", "severity": "critical"},
        {"id": "CWE-862", "name": "Missing Authorization", "severity": "critical"},
        {"id": "CWE-476", "name": "NULL Pointer Dereference", "severity": "major"},
        {"id": "CWE-287", "name": "Improper Authentication", "severity": "critical"},
        {"id": "CWE-190", "name": "Integer Overflow or Wraparound", "severity": "major"},
        {"id": "CWE-502", "name": "Deserialization of Untrusted Data", "severity": "critical"},
        {"id": "CWE-77", "name": "Command Injection", "severity": "critical"},
        {"id": "CWE-119", "name": "Improper Restriction of Operations within Memory Buffer", "severity": "major"},
        {"id": "CWE-798", "name": "Use of Hard-coded Credentials", "severity": "critical"},
        {"id": "CWE-918", "name": "Server-Side Request Forgery (SSRF)", "severity": "critical"},
        {"id": "CWE-306", "name": "Missing Authentication for Critical Function", "severity": "critical"},
        {"id": "CWE-362", "name": "Race Condition", "severity": "major"},
        {"id": "CWE-269", "name": "Improper Privilege Management", "severity": "major"},
        {"id": "CWE-94", "name": "Code Injection", "severity": "critical"},
        {"id": "CWE-863", "name": "Incorrect Authorization", "severity": "critical"},
        {"id": "CWE-276", "name": "Incorrect Default Permissions", "severity": "minor"},
    ]

    @property
    def name(self) -> str:
        return "cwe"

    def fetch(self) -> List[StandardRule]:
        """Fetch CWE data from MITRE zip; fall back to embedded Top 25."""
        entries = self._fetch_from_zip()
        if not entries:
            entries = self._FALLBACK
        rules = []
        for entry in entries:
            rules.append(StandardRule(
                id=entry["id"].replace("-", "_").lower(),
                name=entry["name"],
                description=f"{entry['id']}: {entry['name']}",
                severity=entry.get("severity", "major"),
                languages=["python", "javascript", "typescript", "java", "go", "csharp"],
                pattern="",
                remediation=f"See MITRE {entry['id']} for remediation guidance.",
                source="CWE"
            ))
        return rules

    def _fetch_from_zip(self) -> List[dict]:
        """Download and parse the MITRE CWE JSON zip.

        Extracts Weakness entries from the top-level JSON file.
        Returns empty list on any failure so the caller uses the fallback.
        """
        try:
            resp = requests.get(self._URL, timeout=30, stream=True)
            resp.raise_for_status()
            raw = resp.content
        except requests.RequestException:
            return []

        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                json_names = [n for n in zf.namelist() if n.endswith('.json')]
                if not json_names:
                    return []
                with zf.open(json_names[0]) as jf:
                    data = json.load(jf)
        except (zipfile.BadZipFile, json.JSONDecodeError, KeyError):
            return []

        entries = []
        try:
            weaknesses = (
                data.get("Weakness_Catalog", {})
                    .get("Weaknesses", {})
                    .get("Weakness", [])
            )
            for w in weaknesses[:200]:  # cap at 200 to limit memory usage
                cwe_id = f"CWE-{w.get('@ID', '0')}"
                name = w.get("@Name", "Unknown")
                desc = w.get("Description", name)
                # Classify severity by likelihood/impact if available
                severity = "major"
                likelihood = w.get("Likelihood_Of_Exploit", "").lower()
                if likelihood in ("high", "very high"):
                    severity = "critical"
                elif likelihood in ("low", "very low"):
                    severity = "minor"
                entries.append({
                    "id": cwe_id, "name": name,
                    "description": desc, "severity": severity,
                })
        except (TypeError, AttributeError):
            return []

        return entries if entries else []


class EPSSSource(StandardSource):
    """
    Fetcher for EPSS (Exploit Prediction Scoring System) top scores from FIRST.org.
    Returns top 100 CVEs by exploit probability — used to prioritise SCA findings.
    """

    _URL = "https://api.first.org/data/v1/epss?limit=100&order=!epss"

    @property
    def name(self) -> str:
        return "epss"

    def fetch(self) -> List[StandardRule]:
        try:
            resp = requests.get(self._URL, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError):
            return []

        rules = []
        for item in data.get("data", []):
            cve = item.get("cve", "")
            epss_score = float(item.get("epss", 0))
            percentile = float(item.get("percentile", 0))
            severity = "critical" if epss_score >= 0.5 else "major"
            rules.append(StandardRule(
                id=cve.lower().replace("-", "_"),
                name=f"{cve} (EPSS {epss_score:.4f})",
                description=(
                    f"{cve} has an EPSS exploit probability of "
                    f"{epss_score:.1%} (top {(1 - percentile):.1%} of CVEs)."
                ),
                severity=severity,
                languages=[],
                pattern="",
                remediation=f"Patch or mitigate {cve} immediately — high exploit probability.",
                source="EPSS"
            ))
        return rules


class SourceManager:
    """Manages multiple sources."""

    def __init__(self):
        self.sources: Dict[str, StandardSource] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.sources['gsf'] = GSFSource()
        self.sources['ecocode'] = EcoCodeSource()
        self.sources['owasp'] = OWASPTop10Source()
        self.sources['cwe'] = CWESource()
        self.sources['epss'] = EPSSSource()

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
