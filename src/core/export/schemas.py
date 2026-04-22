from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from src.version import __version__


class ExportMetadata(BaseModel):
    exported_at: str
    project_name: str
    version: str = __version__
    total_files: Optional[int] = None
    language: Optional[str] = None
    path: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Issue(BaseModel):
    id: str
    type: str = "green_violation"
    severity: str
    message: str
    file: str
    line: int
    remediation: Optional[str] = None
    ai_suggestion: Optional[str] = None
    effort: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    carbon_impact: Optional[float] = None
    energy_factor: Optional[Union[float, int, str]] = None
    name: Optional[str] = None
    # AI sustainability fields (EPIC-28)
    category: Optional[str] = None
    co2_note: Optional[str] = None
    provider: Optional[str] = None
    model_tier: Optional[str] = None
    estimated_co2_g: Optional[float] = None

    model_config = ConfigDict(extra='ignore')


class ScanResultSchema(BaseModel):
    issues: List[Issue]
    scanning_emissions: float
    codebase_emissions: float
    per_file_emissions: Dict[str, float] = Field(default_factory=dict)
    metadata: ExportMetadata

    model_config = ConfigDict(extra='ignore')
