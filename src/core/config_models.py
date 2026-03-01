"""
Pydantic models for Green-AI configuration.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class Severity(str, Enum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"

class RulesConfig(BaseModel):
    enabled: List[str] = Field(default_factory=list, description="List of explicitly enabled rule IDs")
    disabled: List[str] = Field(default_factory=list, description="List of explicitly disabled rule IDs")
    severity: Dict[str, Severity] = Field(default_factory=dict, description="Override severity for specific rules")

class RateLimitConfig(BaseModel):
    tpm: int = Field(default=10000, description="Tokens per minute")
    rpm: int = Field(default=500, description="Requests per minute")

class LlmConfig(BaseModel):
    provider: str = Field(default="openai", description="LLM provider (openai, anthropic, etc.)")
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig, description="Rate limiting settings")

class CacheConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable disk caching")
    path: str = Field(default=".green-ai/cache", description="Path to cache directory")
    ttl: int = Field(default=86400, description="Cache TTL in seconds")

class GreenAIConfig(BaseModel):
    languages: List[str] = Field(
        default_factory=lambda: ['python', 'javascript', 'typescript', 'java', 'go'],
        description="List of enabled languages"
    )
    rules: RulesConfig = Field(default_factory=RulesConfig, description="Rule configuration")
    standards: List[str] = Field(default_factory=list, description="Compliance standards to check against")
    ignore_files: List[str] = Field(
        default_factory=lambda: ['*.pyc', '__pycache__', '.git', '.venv', 'node_modules', 'dist', 'build'],
        description="Glob patterns for files/directories to ignore"
    )
    auto_fix: bool = Field(default=False, description="Whether to auto-apply fixes")
    llm: LlmConfig = Field(default_factory=LlmConfig, description="LLM integration settings")
    concurrency: Optional[int] = Field(default=None, description="Number of parallel workers")
    chunk_size: Optional[int] = Field(default=None, description="Chunk size for parallel processing")
    cache: CacheConfig = Field(default_factory=CacheConfig, description="Cache settings")
