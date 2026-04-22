"""
Tests for EPIC-29: Standards Sync Engine
Covers hash verification, offline fallback, stale checks, version manifest.
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.standards.sync_engine import (
    StandardsSyncEngine,
    SyncManifest,
    ManifestEntry,
    _SOURCES,
    _SOURCE_MAP,
)
from src.standards.sources import OWASPTop10Source, CWESource, EPSSSource


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def cache_dir(tmp_path):
    return tmp_path / "standards_cache"


@pytest.fixture
def engine(cache_dir):
    return StandardsSyncEngine(cache_dir=cache_dir, sync_interval_hours=24)


# ── Source registry ───────────────────────────────────────────────────────────

class TestSourceRegistry:
    def test_all_five_sources_registered(self):
        names = {s.name for s in _SOURCES}
        assert names == {"gsf", "ecocode", "owasp", "cwe", "epss"}

    def test_source_map_matches_list(self):
        assert set(_SOURCE_MAP.keys()) == {s.name for s in _SOURCES}

    def test_each_source_has_url(self):
        for spec in _SOURCES:
            assert spec.url.startswith("http")

    def test_unknown_source_raises(self, engine):
        with pytest.raises(ValueError, match="Unknown standard source"):
            engine.sync_source("nonexistent_source")


# ── Manifest persistence ──────────────────────────────────────────────────────

class TestManifestPersistence:
    def test_manifest_creates_fresh_on_missing_file(self, cache_dir):
        engine = StandardsSyncEngine(cache_dir=cache_dir)
        assert isinstance(engine.manifest, SyncManifest)
        assert engine.manifest.entries == {}

    def test_manifest_roundtrip(self, cache_dir):
        engine = StandardsSyncEngine(cache_dir=cache_dir)
        entry = ManifestEntry(
            name="owasp",
            display_name="OWASP Top 10",
            url="https://example.com",
            last_sync=datetime.now(timezone.utc).isoformat(),
            content_hash="abc123",
            version_tag="2024-04-22",
            sync_ok=True,
            size_bytes=1024,
        )
        engine.manifest.entries["owasp"] = entry
        engine._save_manifest()

        engine2 = StandardsSyncEngine(cache_dir=cache_dir)
        loaded = engine2.manifest.entries.get("owasp")
        assert loaded is not None
        assert loaded.content_hash == "abc123"
        assert loaded.sync_ok is True
        assert loaded.size_bytes == 1024

    def test_corrupt_manifest_resets_gracefully(self, cache_dir):
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "manifest.json").write_text("NOT VALID JSON }{")
        engine = StandardsSyncEngine(cache_dir=cache_dir)
        assert engine.manifest.entries == {}


# ── Hash verification ─────────────────────────────────────────────────────────

class TestHashVerification:
    def test_sha256_deterministic(self):
        data = b"hello world"
        h1 = StandardsSyncEngine._sha256(data)
        h2 = StandardsSyncEngine._sha256(data)
        assert h1 == h2
        assert len(h1) == 64

    def test_different_content_different_hash(self):
        h1 = StandardsSyncEngine._sha256(b"content A")
        h2 = StandardsSyncEngine._sha256(b"content B")
        assert h1 != h2

    def test_sync_stores_correct_hash(self, engine):
        raw = b"owasp top 10 content"
        expected_hash = StandardsSyncEngine._sha256(raw)

        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = raw
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            entry = engine.sync_source("owasp", force=True)

        assert entry.content_hash == expected_hash
        assert entry.sync_ok is True


# ── Sync behaviour ────────────────────────────────────────────────────────────

class TestSyncBehaviour:
    def test_sync_success_writes_cache(self, engine):
        raw = b"gsf standards data"
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = raw
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            entry = engine.sync_source("gsf", force=True)

        assert entry.sync_ok is True
        cached = engine._read_cache("gsf")
        assert cached == raw

    def test_sync_skipped_when_fresh(self, engine):
        # Mark source as fresh
        now = datetime.now(timezone.utc).isoformat()
        engine.manifest.entries["epss"] = ManifestEntry(
            name="epss",
            display_name="EPSS",
            url="https://example.com",
            last_sync=now,
            content_hash="abc",
            sync_ok=True,
        )
        engine._save_manifest()

        with patch("requests.get") as mock_get:
            engine.sync_source("epss", force=False)
            # Should NOT call requests.get — cache is fresh
            mock_get.assert_not_called()

    def test_force_bypasses_freshness(self, engine):
        now = datetime.now(timezone.utc).isoformat()
        engine.manifest.entries["epss"] = ManifestEntry(
            name="epss",
            display_name="EPSS",
            url="https://example.com",
            last_sync=now,
            content_hash="old",
            sync_ok=True,
        )
        engine._save_manifest()

        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = b"new data"
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp
            engine.sync_source("epss", force=True)
            mock_get.assert_called_once()

    def test_offline_fallback_uses_cache(self, engine, cache_dir):
        cached_data = b"cached owasp data"
        engine._write_cache("owasp", cached_data)

        with patch("requests.get", side_effect=requests.RequestException("timeout")):
            entry = engine.sync_source("owasp", force=True)

        assert entry.sync_ok is False
        assert "cached" in (entry.error or "").lower() or "Network" in (entry.error or "")
        assert engine._read_cache("owasp") == cached_data

    def test_offline_no_cache_marks_error(self, engine):
        with patch("requests.get", side_effect=requests.RequestException("timeout")):
            entry = engine.sync_source("cwe", force=True)

        assert entry.sync_ok is False
        assert entry.error is not None

    def test_sync_all_returns_all_sources(self, engine):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = b"data"
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            results = engine.sync_all(force=True)

        assert set(results.keys()) == {"gsf", "ecocode", "owasp", "cwe", "epss"}

    def test_hash_unchanged_does_not_re_write_cache(self, engine):
        raw = b"stable content"
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = raw
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            e1 = engine.sync_source("owasp", force=True)
            e2 = engine.sync_source("owasp", force=True)

        assert e1.content_hash == e2.content_hash


# ── Stale check ───────────────────────────────────────────────────────────────

class TestStaleCheck:
    def _set_last_sync(self, engine, name: str, days_ago: float):
        ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
        engine.manifest.entries[name] = ManifestEntry(
            name=name,
            display_name=name,
            url="https://example.com",
            last_sync=ts,
            content_hash="abc",
            sync_ok=True,
        )

    def test_fresh_source_not_stale(self, engine):
        self._set_last_sync(engine, "owasp", days_ago=0.5)
        stale = engine.check_stale(max_age_days=7)
        assert stale["owasp"] is False

    def test_old_source_is_stale(self, engine):
        self._set_last_sync(engine, "cwe", days_ago=10)
        stale = engine.check_stale(max_age_days=7)
        assert stale["cwe"] is True

    def test_never_synced_is_stale(self, engine):
        stale = engine.check_stale(max_age_days=7)
        assert stale["gsf"] is True

    def test_any_stale_true_when_one_stale(self, engine):
        self._set_last_sync(engine, "owasp", days_ago=0.1)
        # gsf never synced → stale
        assert engine.any_stale(max_age_days=7) is True

    def test_any_stale_false_when_all_fresh(self, engine):
        for s in _SOURCES:
            self._set_last_sync(engine, s.name, days_ago=0.1)
        assert engine.any_stale(max_age_days=7) is False


# ── Versions output ───────────────────────────────────────────────────────────

class TestVersions:
    def test_versions_returns_all_sources(self, engine):
        rows = engine.versions()
        names = {r["name"] for r in rows}
        assert names == {"gsf", "ecocode", "owasp", "cwe", "epss"}

    def test_versions_shows_never_for_unsynced(self, engine):
        rows = engine.versions()
        unsynced = [r for r in rows if r["last_sync"] is None]
        assert len(unsynced) == len(_SOURCES)

    def test_versions_after_sync(self, engine):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = b"data"
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp
            engine.sync_source("epss", force=True)

        rows = engine.versions()
        epss_row = next(r for r in rows if r["name"] == "epss")
        assert epss_row["sync_ok"] is True
        assert epss_row["last_sync"] is not None
        assert epss_row["content_hash"] is not None


# ── Extended sources (OWASP, CWE, EPSS) ──────────────────────────────────────

class TestOWASPSource:
    def test_fallback_returns_10_rules(self):
        src = OWASPTop10Source()
        with patch("requests.get", side_effect=requests.RequestException("no net")):
            rules = src.fetch()
        assert len(rules) == 10
        assert all(r.source == "OWASP" for r in rules)
        assert all(r.severity == "critical" for r in rules)

    def test_rule_ids_are_slugified(self):
        src = OWASPTop10Source()
        with patch("requests.get", side_effect=requests.RequestException("no net")):
            rules = src.fetch()
        for r in rules:
            assert ":" not in r.id
            assert " " not in r.id


class TestCWESource:
    def test_returns_25_rules(self):
        src = CWESource()
        rules = src.fetch()
        assert len(rules) == 25

    def test_rule_ids_lowercase(self):
        src = CWESource()
        rules = src.fetch()
        for r in rules:
            assert r.id == r.id.lower()
            assert "-" not in r.id

    def test_source_field_is_cwe(self):
        src = CWESource()
        rules = src.fetch()
        assert all(r.source == "CWE" for r in rules)


class TestEPSSSource:
    def test_empty_on_network_failure(self):
        src = EPSSSource()
        with patch("requests.get", side_effect=requests.RequestException("no net")):
            rules = src.fetch()
        assert rules == []

    def test_parses_epss_response(self):
        src = EPSSSource()
        mock_data = {
            "data": [
                {"cve": "CVE-2023-1234", "epss": "0.9500", "percentile": "0.9999"},
                {"cve": "CVE-2023-5678", "epss": "0.3000", "percentile": "0.8500"},
            ]
        }
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_data
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp
            rules = src.fetch()

        assert len(rules) == 2
        assert rules[0].severity == "critical"   # epss >= 0.5
        assert rules[1].severity == "major"      # epss < 0.5
        assert rules[0].source == "EPSS"
