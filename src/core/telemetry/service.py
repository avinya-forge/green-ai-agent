import uuid
import platform
import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from src.utils.logger import logger
from .schemas import ScanMetrics, TelemetryEvent

class TelemetryService:
    """
    Singleton service for collecting and managing telemetry data.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        # Default to enabled, but respect env var
        self.enabled = os.getenv('GREEN_AI_TELEMETRY', 'true').lower() == 'true'

        # Check if anonymization is required (default true)
        self.anonymize = os.getenv('GREEN_AI_ANONYMIZE', 'true').lower() == 'true'

        self.session_id = str(uuid.uuid4())
        self.events: List[TelemetryEvent] = []

        # Define storage path
        self.storage_path = Path('output/telemetry.jsonl')

    def track_scan(self,
                   project_id: str,
                   duration: float,
                   language: str,
                   violations: List[Dict[str, Any]],
                   codebase_emissions: float,
                   scanning_emissions: float):
        """Record metrics for a completed scan."""
        if not self.enabled:
            return

        # Anonymize project ID if needed
        safe_project_id = self._anonymize(project_id) if self.anonymize else project_id

        # Calculate aggregations
        by_severity = {}
        by_rule = {}

        for v in violations:
            sev = v.get('severity', 'unknown')
            rid = v.get('id', 'unknown')
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_rule[rid] = by_rule.get(rid, 0) + 1

        metrics = ScanMetrics(
            project_id=safe_project_id,
            scan_id=str(uuid.uuid4()),
            duration_seconds=duration,
            language=language,
            total_violations=len(violations),
            violations_by_severity=by_severity,
            violations_by_rule=by_rule,
            codebase_emissions=codebase_emissions,
            scanning_emissions=scanning_emissions,
            ci_environment=os.getenv('CI') is not None,
            os_system=platform.system(),
            python_version=platform.python_version()
        )

        self._record_event('scan_complete', metrics.model_dump())
        logger.debug(f"Telemetry: Scan recorded (ID: {metrics.scan_id})")

    def track_error(self, error_type: str, message: str):
        """Record an error event."""
        if not self.enabled:
            return

        self._record_event('error', {
            'type': error_type,
            'message': message
        })

    def _record_event(self, event_type: str, payload: Dict[str, Any]):
        """Internal method to store event."""
        event = TelemetryEvent(
            event_type=event_type,
            payload=payload,
            user_id=None # TODO: Implement user identification logic
        )
        self.events.append(event)

        # Persist to local storage immediately
        self._persist_event(event)

    def _persist_event(self, event: TelemetryEvent):
        """Append event to local JSONL file."""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.storage_path, 'a', encoding='utf-8') as f:
                f.write(event.model_dump_json() + '\n')

        except Exception as e:
            # Don't crash the app if telemetry fails
            logger.debug(f"Telemetry: Failed to persist event: {e}")

    def _anonymize(self, value: str) -> str:
        """Anonymize sensitive values using SHA256."""
        if not value:
            return ""
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def export_events(self, output_path: str = 'output/telemetry.json'):
        """Dump all in-memory events to a JSON file (legacy export)."""
        if not self.enabled:
            return

        # Ensure directory exists
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = [e.model_dump(mode='json') for e in self.events]

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Telemetry: Exported {len(data)} events to {path}")
        except Exception as e:
            logger.error(f"Telemetry: Failed to export events: {e}")
