"""
Dictionary utility functions.
"""

from typing import Dict, Any

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries.

    Args:
        base: The base dictionary (will be copied, not modified in place).
        override: The dictionary with values to override/merge.

    Returns:
        A new dictionary with merged content.
    """
    if not isinstance(base, dict):
        return override

    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result
