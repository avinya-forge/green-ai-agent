from typing import Dict, Optional, List
import logging
from src.core.remediation.base import RemediationStrategy

logger = logging.getLogger(__name__)


class RemediationEngine:
    """
    Orchestrates remediation strategies.

    This engine replaces the legacy AISuggester and RemediationAgent.
    It maintains a registry of strategies mapped by rule ID.
    """

    def __init__(self):
        self._strategies: Dict[str, RemediationStrategy] = {}
        self._load_strategies()

    def _load_strategies(self):
        """Register all available remediation strategies."""
        # Import strategies here to avoid circular imports
        # In a real dynamic system, this could use plugin discovery
        try:
            from src.core.remediation.strategies.python import (
                ListAppendToComprehension,
                EnumerateTransformer,
                UnnecessaryComprehensionTransformer
            )

            self.register_strategy(ListAppendToComprehension())
            self.register_strategy(EnumerateTransformer())
            self.register_strategy(UnnecessaryComprehensionTransformer())

        except ImportError:
            logger.warning("Could not load Python remediation strategies. Ensure libcst is installed.")
        except Exception as e:
            logger.error(f"Error loading remediation strategies: {e}")

    def register_strategy(self, strategy: RemediationStrategy):
        """Register a new strategy."""
        self._strategies[strategy.rule_id] = strategy
        logger.debug(f"Registered remediation strategy for rule: {strategy.rule_id}")

    def get_suggestion(self, rule_id: str) -> str:
        """
        Get a text suggestion for a given rule.
        Returns a generic message if no strategy is found.
        """
        strategy = self._strategies.get(rule_id)
        if strategy:
            return strategy.get_suggestion()

        # Fallback messages based on common patterns
        if 'loop' in rule_id:
            return "Consider optimizing the loop structure or using vectorization."
        if 'compute' in rule_id:
            return "Cache results or move computation out of critical path."

        return "Review code for potential optimization."

    def get_diff(self, file_path: str, code: str, line: int, rule_id: str) -> Optional[str]:
        """
        Get a code diff for the suggested fix.
        Returns None if no strategy exists or fix fails.
        """
        strategy = self._strategies.get(rule_id)
        if not strategy:
            logger.debug(f"No strategy found for rule {rule_id}")
            return None

        try:
            return strategy.get_diff(file_path, code, line)
        except Exception as e:
            logger.error(f"Error generating diff for {rule_id} at {file_path}:{line}: {e}")
            return None

    # Legacy compatibility methods
    def suggest_fix(self, issue: Dict) -> str:
        """Compatibility method for scanner.py (replaces AISuggester.suggest_fix)."""
        rule_id = issue.get('id', 'unknown')
        return self.get_suggestion(rule_id)

    def get_remediation_diff(self, file_path: str, line: int, issue_id: str, original_code: str) -> str:
        """Compatibility method for UI (replaces RemediationAgent.get_remediation_diff)."""
        diff = self.get_diff(file_path, original_code, line, issue_id)
        return diff if diff else ""

    def fix_file(self, file_path: str, violations: List[Dict]) -> Dict[str, int]:
        """
        Apply fixes to a file for the given violations.

        Args:
            file_path: Path to the file to fix.
            violations: List of violations to fix.

        Returns:
            Dictionary with 'fixed' and 'failed' counts.
        """
        fixed_count = 0
        failed_count = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {'fixed': 0, 'failed': len(violations)}

        # Sort violations bottom-up to preserve line numbers for earlier fixes
        sorted_violations = sorted(violations, key=lambda x: x.get('line', 0), reverse=True)

        current_code = content
        # Track modified lines to prevent overlapping fixes
        # Simple heuristic: if we fixed a line, we might have invalidated nearby lines.
        # But LibCST handles AST, so "line" is just for locating the node.
        # If we change the AST, line numbers shift. But since we go bottom-up,
        # changes only affect subsequent lines (which we already processed).
        # So this should be safe for independent violations.

        for violation in sorted_violations:
            rule_id = violation.get('id')
            line = violation.get('line')

            strategy = self._strategies.get(rule_id)
            if not strategy:
                failed_count += 1
                continue

            try:
                new_code = strategy.apply_fix(current_code, line)
                if new_code and new_code != current_code:
                    current_code = new_code
                    fixed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error applying fix for {rule_id} at {file_path}:{line}: {e}")
                failed_count += 1

        if fixed_count > 0:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(current_code)
            except Exception as e:
                logger.error(f"Failed to write fixed file {file_path}: {e}")

        return {'fixed': fixed_count, 'failed': failed_count}
