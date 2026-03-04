import pytest
import os
import yaml
from src.core.config import ConfigLoader
from src.core.llm.factory import LLMFactory
from src.core.llm.openai_provider import OpenAIProvider
from src.core.llm.mock_provider import MockLLMProvider
from unittest.mock import patch, MagicMock

def test_config_loader_llm_defaults():
    loader = ConfigLoader()
    config = loader.load()

    assert 'llm' in config
    assert config['llm']['provider'] == 'openai'

@patch('src.core.llm.factory.load_config')
def test_llm_factory_uses_config(mock_load_config):
    # Mock config
    mock_load_config.return_value = {
        'llm': {
            'provider': 'mock',
            'rate_limit': {
                'tpm': 100,
                'rpm': 10
            }
        }
    }

    provider = LLMFactory.get_provider() # Should use config default "mock"

    assert isinstance(provider, MockLLMProvider)
    assert provider.rate_limiter is not None
    assert provider.rate_limiter.tpm_capacity == 100
    assert provider.rate_limiter.rpm_capacity == 10

@patch('src.core.llm.factory.load_config')
def test_llm_factory_override_config(mock_load_config):
    # Mock config says mock
    mock_load_config.return_value = {
        'llm': {
            'provider': 'mock'
        }
    }

    # Override with openai
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        provider = LLMFactory.get_provider("openai")
        assert isinstance(provider, OpenAIProvider)
