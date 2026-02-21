import pytest
import time
from unittest.mock import patch, MagicMock
from src.core.llm.factory import LLMFactory
from src.core.llm.mock_provider import MockLLMProvider
from src.core.llm.rate_limiter import TokenBucketRateLimiter
from src.core.llm.usage import TokenUsage

class TestLLMIntegration:

    def test_mock_provider_flow(self):
        """
        Test the full flow of using a Mock provider via factory.
        [LLM-015] Integration Test: OpenAI Mock (using MockLLMProvider as proxy)
        """
        config = {
            'llm': {
                'provider': 'mock',
                'rate_limit': {'tpm': 10000, 'rpm': 500}
            }
        }

        provider = LLMFactory.get_provider(config=config)
        assert isinstance(provider, MockLLMProvider)

        snippet = "for i in range(10): pass"
        fix = provider.generate_fix(snippet, "inefficient loop", language="python")

        assert fix is not None
        assert "Optimized loop" in fix or "Mock fix" in fix

        usage = provider.get_total_usage()
        assert usage.total_tokens > 0
        assert usage.cost >= 0.0

    def test_token_usage_accumulation(self):
        """
        Test that token usage accumulates across multiple calls.
        [LLM-016] Integration Test: Token Logic
        """
        provider = MockLLMProvider()

        # Initial usage should be 0
        initial_usage = provider.get_total_usage()
        assert initial_usage.total_tokens == 0

        # First call
        provider.generate_fix("code1", "violation1")
        # Capture values as provider.usage is mutable
        usage1_total = provider.get_total_usage().total_tokens
        assert usage1_total > 0

        # Second call
        provider.generate_fix("code2", "violation2")
        usage2 = provider.get_total_usage()

        assert usage2.total_tokens > usage1_total

    @patch('src.core.llm.rate_limiter.time')
    def test_rate_limiter_logic(self, mock_time):
        """
        Test that rate limiter triggers sleep when limits are exceeded.
        [LLM-017] Integration Test: Rate Limit Logic
        """
        # Mock time.time to return increments
        # Start at 0
        current_time = [0.0]

        def fake_time():
            return current_time[0]

        def fake_sleep(seconds):
            current_time[0] += seconds

        mock_time.time.side_effect = fake_time
        mock_time.sleep.side_effect = fake_sleep

        # Configure a very restrictive limiter: 1 request per minute
        limiter = TokenBucketRateLimiter(tpm=1000, rpm=1)

        # Force limiter's last_check to match our fake start time
        limiter.last_check = 0.0

        # Consume 1 request (capacity is 1)
        limiter.wait_for(estimated_tokens=10)

        # Next request should trigger sleep
        # It needs to wait ~60 seconds to refill 1 request
        limiter.wait_for(estimated_tokens=10)

        # Verify time advanced
        assert current_time[0] >= 60.0
        mock_time.sleep.assert_called()
