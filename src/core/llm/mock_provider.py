from typing import Optional, Dict
from .provider import LLMProvider

class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing purposes.
    """

    def __init__(self, api_key: str = "mock-key", responses: Optional[Dict[str, str]] = None):
        """
        Initialize the mock provider.

        Args:
            api_key: Mock API key (ignored).
            responses: Dictionary of pre-canned responses.
                       Keys can be "fix", "explanation", "cost".
        """
        super().__init__(api_key)
        self.responses = responses or {}

    def generate_fix(self, code_snippet: str, violation_description: str) -> Optional[str]:
        """
        Return a mock fix.
        """
        return self.responses.get("fix", f"# Mock fix applied to:\n# {code_snippet}")

    def explain_violation(self, code_snippet: str, violation_description: str) -> Optional[str]:
        """
        Return a mock explanation.
        """
        return self.responses.get("explanation", f"Mock explanation for violation: {violation_description}")

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Return a mock cost.
        """
        return float(self.responses.get("cost", 0.0))
