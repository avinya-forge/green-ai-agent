from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class RemediationStrategy(ABC):
    """
    Abstract base class for remediation strategies.
    Each strategy handles a specific type of violation or pattern.
    """

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """The rule ID this strategy addresses."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the strategy."""
        pass

    @abstractmethod
    def get_suggestion(self) -> str:
        """Return a text description of the suggested fix."""
        pass

    @abstractmethod
    def get_diff(self, file_path: str, code: str, line: int) -> Optional[str]:
        """
        Generate a unified diff for the fix.

        Args:
            file_path: Path to the file.
            code: Content of the file.
            line: Line number where the violation occurred (1-based).

        Returns:
            String containing the unified diff, or None if fix cannot be applied.
        """
        pass

    def apply_fix(self, code: str, line: int) -> Optional[str]:
        """
        Apply the fix and return the modified code.

        Args:
            code: Content of the file.
            line: Line number where the violation occurred (1-based).

        Returns:
            Modified code string, or None if fix cannot be applied.
        """
        return None
