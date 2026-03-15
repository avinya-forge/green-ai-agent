from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ScanMetrics(BaseModel):
    """Metrics collected during a single scan."""
    project_id: str = Field(..., description="Unique ID of the project scanned (or name/hash)")
    scan_id: str = Field(..., description="Unique ID for this scan run")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: float = Field(..., description="Total execution time in seconds")
    language: str = Field(..., description="Primary language scanned")

    # Violation counts
    total_violations: int = 0
    violations_by_severity: Dict[str, int] = Field(default_factory=dict)
    violations_by_rule: Dict[str, int] = Field(default_factory=dict)

    # Emissions
    codebase_emissions: float = 0.0
    scanning_emissions: float = 0.0

    # Environment
    ci_environment: bool = False
    os_system: str = "unknown"
    python_version: str = "unknown"


class TelemetryEvent(BaseModel):
    """Generic telemetry event."""
    event_type: str = Field(..., description="Type of event (scan_complete, error, rule_hit)")
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None  # Anonymized user ID if opt-in
