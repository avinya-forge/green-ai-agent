import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple


def load_baseline(baseline_path: str = '.green-ai/baseline.json') -> Optional[Dict]:
    """Load baseline data from file."""
    path = Path(baseline_path)
    if not path.exists():
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def filter_with_baseline(
    issues: List[Dict], baseline: Optional[Dict]
) -> Tuple[List[Dict], int, int]:
    """
    Filter out issues that are already in the baseline.
    Returns (filtered_issues, skipped_count, fixed_count)
    """
    if not baseline:
        return issues, 0, 0

    baseline_fingerprints = {v['fingerprint'] for v in baseline.get('violations', [])}
    filtered = []
    skipped = 0

    for issue in issues:
        import hashlib
        fingerprint = hashlib.sha256(
            f"{issue.get('id')}:{issue.get('file')}:{issue.get('line')}".encode()
        ).hexdigest()

        if fingerprint in baseline_fingerprints:
            skipped += 1
        else:
            filtered.append(issue)

    # Simple fixed count estimation: items in baseline not in current scan
    # This is a very rough estimate as lines change
    current_fingerprints = {
        hashlib.sha256(
            f"{issue.get('id')}:{issue.get('file')}:{issue.get('line')}".encode()
        ).hexdigest()
        for issue in issues
    }
    fixed = 0
    for bf in baseline_fingerprints:
        if bf not in current_fingerprints:
            fixed += 1

    return filtered, skipped, fixed


def get_violation_fingerprint(issue: Dict[str, Any]) -> str:
    """Create a unique fingerprint for a violation"""
    import hashlib
    return hashlib.sha256(f"{issue.get('id')}:{issue.get('file')}:{issue.get('line')}".encode()).hexdigest()
