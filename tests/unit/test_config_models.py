"""
Tests for Config Models.
"""
import pytest
from src.core.config_models import GreenAIConfig, Severity

def test_config_defaults():
    config = GreenAIConfig()
    assert config.languages == ['python', 'javascript', 'typescript', 'java', 'go']
    assert config.rules.enabled == []
    assert config.llm.provider == "openai"

def test_severity_validation():
    config_data = {
        "rules": {
            "severity": {
                "my_rule": "critical",
                "other_rule": "minor"
            }
        }
    }
    config = GreenAIConfig(**config_data)
    assert config.rules.severity["my_rule"] == Severity.CRITICAL
    assert config.rules.severity["other_rule"] == Severity.MINOR

def test_invalid_severity():
    config_data = {
        "rules": {
            "severity": {
                "my_rule": "invalid_level"
            }
        }
    }
    with pytest.raises(ValueError):
        GreenAIConfig(**config_data)

def test_nested_merge_behavior_simulation():
    # This just tests pydantic model update, not the deep merge utility
    config = GreenAIConfig()
    config.rules.enabled.append("rule1")
    assert "rule1" in config.rules.enabled
