from typing import Optional
from .provider import LLMProvider
from .openai_provider import OpenAIProvider
from .mock_provider import MockLLMProvider
from .rate_limiter import TokenBucketRateLimiter
from src.core.config import load_config
import os


class LLMFactory:
    """
    Factory to create LLM provider instances.
    """

    @staticmethod
    def get_provider(provider_type: Optional[str] = None, api_key: str = None, config: Optional[dict] = None) -> Optional[LLMProvider]:
        """
        Get an LLM provider instance.

        Args:
            provider_type: The type of provider ("openai", "mock").
                           If None, defaults to configuration or "openai".
            api_key: The API key. If None, it tries to read from environment variables.
            config: Optional configuration dictionary. If None, loads from file.

        Returns:
            An LLMProvider instance, or None if unsupported or missing config.
        """
        if config is None:
            config = load_config()

        llm_config = config.get('llm', {}) or {}

        # Override config with args if provided, otherwise use config default
        provider_type = provider_type or llm_config.get('provider', 'openai')
        provider_type = provider_type.lower()

        provider: Optional[LLMProvider] = None

        if provider_type == "openai":
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")

            if not api_key:
                return None

            provider = OpenAIProvider(api_key)

        elif provider_type == "mock":
            provider = MockLLMProvider(api_key or "mock-key")

        if provider:
            # Configure rate limiter
            rate_limits = llm_config.get('rate_limit', {})
            tpm = rate_limits.get('tpm', 10000)
            rpm = rate_limits.get('rpm', 500)

            limiter = TokenBucketRateLimiter(tpm=tpm, rpm=rpm)
            provider.set_rate_limiter(limiter)

            return provider

        return None
