from typing import Optional
from .provider import LLMProvider
from .openai_provider import OpenAIProvider
from .mock_provider import MockLLMProvider
import os

class LLMFactory:
    """
    Factory to create LLM provider instances.
    """

    @staticmethod
    def get_provider(provider_type: str = "openai", api_key: str = None) -> Optional[LLMProvider]:
        """
        Get an LLM provider instance.

        Args:
            provider_type: The type of provider ("openai", "mock").
            api_key: The API key. If None, it tries to read from environment variables.

        Returns:
            An LLMProvider instance, or None if unsupported or missing config.
        """
        provider_type = provider_type.lower()

        if provider_type == "openai":
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")

            if not api_key:
                return None

            return OpenAIProvider(api_key)

        elif provider_type == "mock":
            return MockLLMProvider(api_key or "mock-key")

        return None
