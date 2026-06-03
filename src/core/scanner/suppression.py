import re
import yaml
from pathlib import Path


def get_suppressions(content):
    suppressions = {}
    lines = content.split('\n')
    for i, line in enumerate(lines):
        match = re.search(r'green-ai:\s*ignore\s*next-line\s+([\w,]+)', line)
        if match:
            rule_ids = match.group(1).split(',')
            target_line = i + 2
            for rid in rule_ids:
                rid = rid.strip()
                if target_line not in suppressions:
                    suppressions[target_line] = []
                suppressions[target_line].append(rid)
    return suppressions


def load_external_suppressions():
    suppress_file = Path('.green-ai/suppress.yaml')
    if suppress_file.exists():
        try:
            with open(suppress_file, 'r') as f:
                data = yaml.safe_load(f) or {}
                from datetime import datetime
                now = datetime.now().date()

                valid_suppressions = []
                for s in data.get('suppressions', []):
                    expiry = s.get('expiry')
                    if expiry:
                        if isinstance(expiry, str):
                            expiry = datetime.strptime(expiry, '%Y-%m-%d').date()
                        if expiry < now:
                            continue
                    valid_suppressions.append(s)
                return valid_suppressions
        except Exception:
            return []
    return []


def is_suppressed(issue, inline_suppressions, external_suppressions=None):
    line = issue.get('line')
    rule_id = issue.get('id')
    file_path = str(issue.get('file', ''))

    if line in inline_suppressions:
        if 'all' in inline_suppressions[line] or rule_id in inline_suppressions[line]:
            return True

    if external_suppressions:
        for s in external_suppressions:
            s_rule = s.get('rule_id')
            if s_rule != 'all' and s_rule != rule_id:
                continue

            s_file = s.get('file')
            if s_file:
                # Standardize paths for comparison
                s_file_norm = s_file.replace('\\', '/')
                file_path_norm = file_path.replace('\\', '/')
                if s_file_norm != file_path_norm and not file_path_norm.endswith('/' + s_file_norm):
                    continue

            return True

    return False
