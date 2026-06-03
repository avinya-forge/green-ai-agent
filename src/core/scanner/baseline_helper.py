import json
import hashlib
from pathlib import Path


def get_violation_fingerprint(issue):
    """Create a unique fingerprint for a violation"""
    return hashlib.sha256(f"{issue.get('id')}:{issue.get('file')}:{issue.get('line')}".encode()).hexdigest()


def load_baseline():
    """Load baseline if it exists"""
    baseline_file = Path('.green-ai/baseline.json')
    if baseline_file.exists():
        try:
            with open(baseline_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    return None


def filter_with_baseline(issues, baseline):
    """Filter out issues that are present in the baseline and calculate delta"""
    if not baseline:
        return issues, 0, 0

    baseline_violations = baseline.get('violations', [])
    baseline_fingerprints = {v['fingerprint'] for v in baseline_violations}

    new_issues = []
    baseline_skipped_count = 0

    current_fingerprints = set()
    for issue in issues:
        fp = get_violation_fingerprint(issue)
        current_fingerprints.add(fp)
        if fp in baseline_fingerprints:
            baseline_skipped_count += 1
        else:
            new_issues.append(issue)

    # Calculate "fixed" issues (present in baseline but not in current scan)
    fixed_count = 0
    for bv in baseline_violations:
        if bv['fingerprint'] not in current_fingerprints:
            fixed_count += 1

    return new_issues, baseline_skipped_count, fixed_count
