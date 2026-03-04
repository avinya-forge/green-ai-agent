"""
Pydantic models for Green-AI configuration.
"""

from enum import Enum
from typing import List, Dict
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

class LlmConfig(BaseModel):
    provider: str = Field(default="openai", description="LLM provider (openai, anthropic, etc.)")

class CacheConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable disk caching")
    path: str = Field(default=".green-ai/cache", description="Path to cache directory")

class GreenAIConfig(BaseModel):
    languages: List[str] = Field(
        default_factory=lambda: ['python', 'javascript', 'typescript', 'java', 'go'],
        description="List of enabled languages"
    )
    rules: RulesConfig = Field(default_factory=RulesConfig, description="Rule configuration")
    standards: List[str] = Field(default_factory=list, description="Compliance standards to check against")
    llm: LlmConfig = Field(default_factory=LlmConfig, description="LLM integration settings")
    cache: CacheConfig = Field(default_factory=CacheConfig, description="Cache settings")
