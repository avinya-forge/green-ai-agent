from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import yaml


def get_suppressions(content: str) -> Dict[int, List[str]]:
    """
    Find lines with # green-ai: ignore next-line.
    Returns a dictionary of line_number -> [rule_ids].
    """
    suppressions = {}
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '# green-ai: ignore next-line' in line:
            # Extract rule IDs if present: # green-ai: ignore next-line rule1 rule2
            match = line.split('# green-ai: ignore next-line')[-1].strip()
            # Remove reason="..." if present
            match = match.split('reason=')[0].strip()

            rule_ids = match.split() if match else ['*']
            suppressions[i + 2] = rule_ids
    return suppressions


def load_external_suppressions(path: str = '.green-ai/suppress.yaml') -> Dict[str, Any]:
    """Load suppressions from external YAML file."""
    p = Path(path)
    if not p.exists():
        return {}
    try:
        with open(p, 'r') as f:
            data = yaml.safe_load(f) or {}
            # Handle list under 'suppressions' key
            if isinstance(data, dict) and 'suppressions' in data:
                data = data['suppressions']

            # If it's a list, convert to dict keyed by file
            if isinstance(data, list):
                new_data = {}
                for item in data:
                    if isinstance(item, dict) and 'file' in item:
                        f_path = item['file']
                        if f_path not in new_data:
                            new_data[f_path] = []
                        if 'rule_id' in item:
                            new_data[f_path].append(item['rule_id'])
                        else:
                            new_data[f_path].append('*')
                return new_data
            return data
    except Exception:
        return {}


def is_suppressed(
    issue: Dict,
    inline_suppressions: Union[List[int], Dict[int, List[str]]],
    external_suppressions: Optional[Union[Dict[str, Any], List[Dict]]] = None
) -> bool:
    """Check if an issue is suppressed."""
    if external_suppressions is None:
        external_suppressions = {}

    line = issue.get('line')
    rule_id = issue.get('id', '')

    # 1. Check inline
    if isinstance(inline_suppressions, dict):
        if line in inline_suppressions:
            rules = inline_suppressions[line]
            if '*' in rules or rule_id in rules:
                return True
    elif isinstance(inline_suppressions, list):
        if line in inline_suppressions:
            return True

    # 2. Check external
    if isinstance(external_suppressions, list):
        # Handle legacy list format
        for entry in external_suppressions:
            if entry.get('file') == issue.get('file') and (entry.get('rule_id') == rule_id or entry.get('rule_id') == '*' or entry.get('id') == rule_id):
                return True
        return False

    file_path = issue.get('file', '')
    file_rules = external_suppressions.get(file_path, [])
    if rule_id in file_rules or '*' in file_rules:
        return True

    # Global suppressions
    global_rules = external_suppressions.get('*', [])
    if rule_id in global_rules:
        return True

    return False
