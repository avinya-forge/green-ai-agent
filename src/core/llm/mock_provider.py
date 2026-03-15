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

    def generate_fix(self, code_snippet: str, violation_description: str, language: str = "python") -> Optional[str]:
        """
        Return a mock fix.
        """
        self.track_usage(100, 50)

        # If a specific fix is provided in responses, use it
        if "fix" in self.responses:
            return self.responses["fix"]

        # Otherwise generate a realistic-looking mock fix
        lines = code_snippet.split('\n')
        fixed_lines = []
        for line in lines:
            if "for" in line and ":" in line:
                fixed_lines.append(f"# Optimized loop for {violation_description}")
            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def explain_violation(self, code_snippet: str, violation_description: str, language: str = "python") -> Optional[str]:
        """
        Return a mock explanation.
        """
        self.track_usage(80, 100)
        return self.responses.get("explanation", f"Mock explanation for violation: {violation_description}")

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Return a mock cost.
        """
        return float(self.responses.get("cost", 0.0))
