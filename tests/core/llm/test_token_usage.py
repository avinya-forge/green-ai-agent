import pytest
from src.core.llm.usage import TokenUsage
from src.core.llm.mock_provider import MockLLMProvider
from src.core.llm.openai_provider import OpenAIProvider
from unittest.mock import MagicMock, patch

def test_token_usage_addition():
    u1 = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30, cost=0.1)
    u2 = TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10, cost=0.05)

    u1.add(u2)

    assert u1.prompt_tokens == 15
    assert u1.completion_tokens == 25
    assert u1.total_tokens == 40
    assert abs(u1.cost - 0.15) < 1e-9

def test_mock_provider_usage():
    provider = MockLLMProvider()
    assert provider.usage.total_tokens == 0

    provider.generate_fix("code", "violation")
    assert provider.usage.prompt_tokens == 100
    assert provider.usage.completion_tokens == 50
    assert provider.usage.total_tokens == 150

    provider.explain_violation("code", "violation")
    # Previous (100, 50) + New (80, 100) = (180, 150)
    assert provider.usage.prompt_tokens == 180
    assert provider.usage.completion_tokens == 150
    assert provider.usage.total_tokens == 330

@patch('requests.post')
def test_openai_provider_usage_tracking(mock_post):
    provider = OpenAIProvider(api_key="test-key")

    # Mock response with usage
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'choices': [{'message': {'content': 'Fixed code'}}],
        'usage': {
            'prompt_tokens': 10,
            'completion_tokens': 20,
            'total_tokens': 30
        }
    }
    mock_post.return_value = mock_response

    provider.generate_fix("code", "violation")

    assert provider.usage.prompt_tokens == 10
    assert provider.usage.completion_tokens == 20
    assert provider.usage.total_tokens == 30
    # Cost for gpt-4o (default): 10*0.005/1000 + 20*0.015/1000 = 0.00005 + 0.0003 = 0.00035
    expected_cost = (10/1000 * 0.005) + (20/1000 * 0.015)
    assert abs(provider.usage.cost - expected_cost) < 1e-9
