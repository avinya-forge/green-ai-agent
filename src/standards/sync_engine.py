"""
Standards Sync Engine (EPIC-29)

Automated fetch-validate-store pipeline for live standards:
  - GSF Patterns (Green Software Foundation)
  - ecoCode Rules
  - OWASP Top 10
  - CWE/MITRE
  - EPSS Scores (exploit probability)

Features:
  - Version manifest with SHA-256 hash verification per source
  - Configurable sync interval (default 24h)
  - Offline fallback: uses last cached version when network unavailable
  - fail_on_stale: CI gate that fails if standards are older than N days
  - CLI: green-ai standards sync | list | versions | check
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# Default cache location: project-level .green-ai/standards/
_DEFAULT_CACHE_DIR = Path.home() / ".green-ai" / "standards"
_MANIFEST_FILE = "manifest.json"
_DEFAULT_SYNC_INTERVAL_HOURS = 24
_STALE_THRESHOLD_DAYS = 7  # fail_on_stale default

# ── Source registry ───────────────────────────────────────────────────────────


@dataclass
class SourceSpec:
    name: str
    display_name: str
    url: str
    format: str          # json | yaml | text
    description: str


_SOURCES: List[SourceSpec] = [
    SourceSpec(
        name="gsf",
        display_name="Green Software Foundation Patterns",
        url=(
            "https://api.github.com/repos/Green-Software-Foundation/"
            "patterns/contents/patterns"
        ),
        format="json",
        description="GSF software sustainability patterns",
    ),
    SourceSpec(
        name="ecocode",
        display_name="ecoCode Rules",
        url=(
            "https://api.github.com/repos/green-code-initiative/"
            "ecoCode/contents/ecocode-rules-specifications"
        ),
        format="json",
        description="Green code rules from the ecoCode initiative",
    ),
    SourceSpec(
        name="owasp",
        display_name="OWASP Top 10",
        url=(
            "https://raw.githubusercontent.com/OWASP/"
            "www-project-top-ten/master/docs/index.md"
        ),
        format="text",
        description="OWASP Top 10 web application security risks",
    ),
    SourceSpec(
        name="cwe",
        display_name="CWE/MITRE Top 25",
        url="https://cwe.mitre.org/data/json/cwe_latest.json.zip",
        format="json",
        description="Common Weakness Enumeration from MITRE",
    ),
    SourceSpec(
        name="epss",
        display_name="EPSS Exploit Probability Scores",
        url="https://api.first.org/data/v1/epss?limit=100&order=!epss",
        format="json",
        description="Top exploited CVEs by FIRST.org EPSS score",
    ),
]

_SOURCE_MAP: Dict[str, SourceSpec] = {s.name: s for s in _SOURCES}


# ── Manifest entry ────────────────────────────────────────────────────────────

@dataclass
class ManifestEntry:
    name: str
    display_name: str
    url: str
    last_sync: Optional[str] = None       # ISO-8601 UTC
    content_hash: Optional[str] = None    # SHA-256 of raw fetched bytes
    version_tag: Optional[str] = None     # e.g. "2024-04-22" or ETag
    sync_ok: bool = False
    error: Optional[str] = None
    size_bytes: int = 0


@dataclass
class SyncManifest:
    schema_version: str = "1"
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    entries: Dict[str, ManifestEntry] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "entries": {k: asdict(v) for k, v in self.entries.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SyncManifest":
        entries = {
            k: ManifestEntry(**v) for k, v in data.get("entries", {}).items()
        }
        return cls(
            schema_version=data.get("schema_version", "1"),
            generated_at=data.get("generated_at", ""),
            entries=entries,
        )


# ── Sync Engine ───────────────────────────────────────────────────────────────

class StandardsSyncEngine:
    """
    Fetches, validates, and stores live standards with hash verification.
    All cached content lives in cache_dir; the manifest tracks versions.
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        sync_interval_hours: int = _DEFAULT_SYNC_INTERVAL_HOURS,
        timeout: int = 15,
    ):
        self.cache_dir = Path(cache_dir or _DEFAULT_CACHE_DIR)
        self.sync_interval_hours = sync_interval_hours
        self.timeout = timeout
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = self._load_manifest()

    # ── Manifest persistence ──────────────────────────────────────────────────

    def _manifest_path(self) -> Path:
        return self.cache_dir / _MANIFEST_FILE

    def _load_manifest(self) -> SyncManifest:
        path = self._manifest_path()
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return SyncManifest.from_dict(data)
            except (json.JSONDecodeError, TypeError, KeyError) as exc:
                logger.warning("Corrupt manifest, resetting: %s", exc)
        return SyncManifest()

    def _save_manifest(self) -> None:
        self.manifest.generated_at = datetime.now(timezone.utc).isoformat()
        self._manifest_path().write_text(
            json.dumps(self.manifest.to_dict(), indent=2), encoding="utf-8"
        )

    # ── Cache file helpers ────────────────────────────────────────────────────

    def _cache_path(self, name: str) -> Path:
        return self.cache_dir / f"{name}.cache"

    def _read_cache(self, name: str) -> Optional[bytes]:
        p = self._cache_path(name)
        return p.read_bytes() if p.exists() else None

    def _write_cache(self, name: str, data: bytes) -> None:
        self._cache_path(name).write_bytes(data)

    # ── Staleness helpers ─────────────────────────────────────────────────────

    def _hours_since_sync(self, entry: ManifestEntry) -> Optional[float]:
        if not entry.last_sync:
            return None
        try:
            last = datetime.fromisoformat(entry.last_sync)
            now = datetime.now(timezone.utc)
            return (now - last).total_seconds() / 3600
        except ValueError:
            return None

    def _needs_sync(self, name: str) -> bool:
        entry = self.manifest.entries.get(name)
        if not entry or not entry.sync_ok:
            return True
        hours = self._hours_since_sync(entry)
        return hours is None or hours >= self.sync_interval_hours

    # ── Fetch ─────────────────────────────────────────────────────────────────

    def _fetch(self, spec: SourceSpec) -> Optional[bytes]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        try:
            resp = requests.get(spec.url, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.content
        except requests.RequestException as exc:
            logger.warning("Fetch failed for %s: %s", spec.name, exc)
            return None

    # ── Hash ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    # ── Sync single source ────────────────────────────────────────────────────

    def sync_source(self, name: str, force: bool = False) -> ManifestEntry:
        spec = _SOURCE_MAP.get(name)
        if spec is None:
            raise ValueError(f"Unknown standard source: {name!r}")

        entry = self.manifest.entries.get(name) or ManifestEntry(
            name=spec.name,
            display_name=spec.display_name,
            url=spec.url,
        )

        if not force and not self._needs_sync(name):
            logger.debug("Source %r is fresh, skipping.", name)
            return entry

        raw = self._fetch(spec)
        if raw is None:
            # Offline fallback: keep existing cache
            cached = self._read_cache(name)
            if cached:
                entry.sync_ok = False
                entry.error = "Network unavailable — using cached version"
                logger.warning("Offline fallback for %r", name)
            else:
                entry.sync_ok = False
                entry.error = "Network unavailable and no cache available"
            self.manifest.entries[name] = entry
            self._save_manifest()
            return entry

        new_hash = self._sha256(raw)
        changed = new_hash != entry.content_hash

        if changed:
            self._write_cache(name, raw)
            logger.info("Source %r updated (hash changed).", name)
        else:
            logger.debug("Source %r hash unchanged.", name)

        entry.content_hash = new_hash
        entry.last_sync = datetime.now(timezone.utc).isoformat()
        entry.version_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entry.sync_ok = True
        entry.error = None
        entry.size_bytes = len(raw)
        self.manifest.entries[name] = entry
        self._save_manifest()
        return entry

    # ── Sync all ──────────────────────────────────────────────────────────────

    def sync_all(self, force: bool = False) -> Dict[str, ManifestEntry]:
        results = {}
        for spec in _SOURCES:
            results[spec.name] = self.sync_source(spec.name, force=force)
        return results

    # ── Versions ──────────────────────────────────────────────────────────────

    def versions(self) -> List[dict]:
        rows = []
        for spec in _SOURCES:
            entry = self.manifest.entries.get(spec.name)
            rows.append(
                {
                    "name": spec.name,
                    "display_name": spec.display_name,
                    "last_sync": entry.last_sync if entry else None,
                    "version_tag": entry.version_tag if entry else None,
                    "content_hash": (entry.content_hash[:12] + "…") if entry and entry.content_hash else None,
                    "sync_ok": entry.sync_ok if entry else False,
                    "size_bytes": entry.size_bytes if entry else 0,
                    "error": entry.error if entry else "never synced",
                }
            )
        return rows

    # ── Stale check ───────────────────────────────────────────────────────────

    def check_stale(self, max_age_days: int = _STALE_THRESHOLD_DAYS) -> Dict[str, bool]:
        """
        Returns {source_name: is_stale} for every source.
        A source is stale if last_sync is missing or older than max_age_days.
        Used by fail_on_stale CI gate.
        """
        stale: Dict[str, bool] = {}
        max_hours = max_age_days * 24
        for spec in _SOURCES:
            entry = self.manifest.entries.get(spec.name)
            if not entry or not entry.sync_ok:
                stale[spec.name] = True
                continue
            hours = self._hours_since_sync(entry)
            stale[spec.name] = hours is None or hours >= max_hours
        return stale

    def any_stale(self, max_age_days: int = _STALE_THRESHOLD_DAYS) -> bool:
        return any(self.check_stale(max_age_days).values())

    # ── Read cached content ───────────────────────────────────────────────────

    def get_cached(self, name: str) -> Optional[bytes]:
        """Return raw cached bytes for a source, or None if not cached."""
        return self._read_cache(name)

    def list_sources(self) -> List[SourceSpec]:
        return list(_SOURCES)
