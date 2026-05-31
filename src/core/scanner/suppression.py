import re
import yaml
import os
from pathlib import Path

def get_suppressions(content):
    """
    Parse inline suppressions from content.
    Format: # green-ai: ignore next-line <rule_id> reason="..."
    """
    suppressions = {}
    lines = content.split('\n')
    for i, line in enumerate(lines):
        match = re.search(r'green-ai:\s*ignore\s*next-line\s+([\w,]+)(?:\s+reason="([^"]*)")?', line)
        if match:
            rule_ids = match.group(1).split(',')
            reason = match.group(2) or "No reason provided"
            target_line = i + 2 # next line (1-based index)
            for rid in rule_ids:
                if target_line not in suppressions:
                    suppressions[target_line] = []
                suppressions[target_line].append(rid.strip())
    return suppressions

def load_external_suppressions():
    """Load suppressions from .green-ai/suppress.yaml"""
    suppress_file = Path('.green-ai/suppress.yaml')
    if suppress_file.exists():
        try:
            with open(suppress_file, 'r') as f:
                data = yaml.safe_load(f) or {}
                # Handle auto-expiry
                from datetime import datetime
                now = datetime.now().date()

                valid_suppressions = []
                for s in data.get('suppressions', []):
                    expiry = s.get('expiry')
                    if expiry:
                        if isinstance(expiry, str):
                            expiry = datetime.strptime(expiry, '%Y-%m-%d').date()
                        if expiry < now:
                            continue # Expired
                    valid_suppressions.append(s)
                return valid_suppressions
        except Exception:
            return []
    return []

def is_suppressed(issue, inline_suppressions, external_suppressions=None):
    """Check if an issue is suppressed by inline comments or external yaml"""
    line = issue.get('line')
    rule_id = issue.get('id')
    file_path = issue.get('file')

    # 1. Inline check
    if line in inline_suppressions:
        if 'all' in inline_suppressions[line] or rule_id in inline_suppressions[line]:
            return True

    # 2. External check (BASE-004)
    if external_suppressions:
        for s in external_suppressions:
            # Check rule match
            s_rule = s.get('rule_id')
            if s_rule != 'all' and s_rule != rule_id:
                continue

            # Check file match
            s_file = s.get('file')
            if s_file:
                if s_file != file_path and not str(file_path).endswith(s_file):
                    continue

            return True

    return False
