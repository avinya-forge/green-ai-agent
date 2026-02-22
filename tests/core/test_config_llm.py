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
    assert config['llm']['rate_limit']['tpm'] == 10000
    assert config['llm']['rate_limit']['rpm'] == 500

def test_config_loader_llm_validation_error():
    loader = ConfigLoader()
    # Inject bad config
    bad_config = {
        'llm': {
            'rate_limit': {
                'tpm': 'not-an-int'
            }
        }
    }

    # We need to bypass merge logic to inject bad types or mock validation
    # Easier: Create a temporary file

    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        yaml.dump(bad_config, tmp)
        tmp_path = tmp.name

    try:
        loader = ConfigLoader(tmp_path)
        with pytest.raises(Exception) as excinfo:
            loader.load()
        # Pydantic error message
        assert "Input should be a valid integer" in str(excinfo.value)
    finally:
        os.remove(tmp_path)

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
