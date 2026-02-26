from pydantic import BaseModel, field_validator
from typing import Optional
from src.utils.security import sanitize_project_name, sanitize_path, is_safe_git_url

class ScanRequest(BaseModel):
    project_name: str
    language: str
    git_url: Optional[str] = None
    path: Optional[str] = None

    @field_validator('project_name')
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Sanitize project name."""
        return sanitize_project_name(v)

    @field_validator('git_url')
    @classmethod
    def validate_git_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate git URL."""
        if v is None:
            return None
        if not is_safe_git_url(v):
            raise ValueError(f"Invalid or unsafe git URL: {v}")
        return v

    @field_validator('path')
    @classmethod
    def validate_path(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize path."""
        if v is None:
            return None
        # sanitize_path returns a Path object, we need string
        try:
            # We allow absolute paths as per CLI logic, but strictness depends on deployment.
            # Here we just sanitize.
            sanitized = sanitize_path(v, allow_absolute=True)
            return str(sanitized)
        except ValueError as e:
            raise ValueError(f"Invalid path: {e}")
