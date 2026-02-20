from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """

    def __init__(self, api_key: str, model: str = None):
        """
        Initialize the provider.

        Args:
            api_key: The API key for the provider.
            model: The model to use (optional, defaults to provider specific).
        """
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def generate_fix(self, code_snippet: str, violation_description: str) -> Optional[str]:
        """
        Generate a fix for a given code violation.

        Args:
            code_snippet: The problematic code snippet.
            violation_description: Description of the violation.

        Returns:
            The suggested fix as a string, or None if generation failed.
        """
        pass

    @abstractmethod
    def explain_violation(self, code_snippet: str, violation_description: str) -> Optional[str]:
        """
        Explain why a piece of code is a violation.

        Args:
            code_snippet: The problematic code snippet.
            violation_description: Description of the violation.

        Returns:
            An explanation string.
        """
        pass

    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate the cost of a request.

        Args:
            prompt_tokens: Number of input tokens.
            completion_tokens: Number of output tokens.

        Returns:
            Estimated cost in USD.
        """
        pass
