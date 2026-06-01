import click
import json
import os
import hashlib
from pathlib import Path
from src.core.scanner.main import Scanner

@click.group()
def baseline():
    """Manage scan baselines to acknowledge technical debt"""
    pass

def _get_violation_fingerprint(issue):
    """Create a unique fingerprint for a violation"""
    return hashlib.sha256(f"{issue.get('id')}:{issue.get('file')}:{issue.get('line')}".encode()).hexdigest()

@baseline.command('create')
@click.argument('path', type=click.Path(exists=True))
@click.option('--language', default='python', help='Language to scan')
def baseline_create(path, language):
    """Scan and create a baseline from current violations"""
    click.echo(f"Creating baseline for {path}...")
    # Temporarily disable baseline loading to get a full scan for the baseline itself
    if Path('.green-ai/baseline.json').exists():
        os.rename('.green-ai/baseline.json', '.green-ai/baseline.json.bak')

    try:
        scanner = Scanner(language=language)
        results = scanner.scan(path)

        issues = results.get('issues', [])
        baseline_data = {
            'project_path': str(Path(path).resolve()),
            'language': language,
            'violations': []
        }

        for issue in issues:
            baseline_data['violations'].append({
                'id': issue.get('id'),
                'file': issue.get('file'),
                'line': issue.get('line'),
                'fingerprint': _get_violation_fingerprint(issue)
            })

        baseline_dir = Path('.green-ai')
        baseline_dir.mkdir(exist_ok=True)
        baseline_file = baseline_dir / 'baseline.json'

        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)

        click.echo(f"[OK] Baseline created with {len(issues)} violations at {baseline_file}")
    finally:
        if Path('.green-ai/baseline.json.bak').exists():
            if not Path('.green-ai/baseline.json').exists():
                 os.rename('.green-ai/baseline.json.bak', '.green-ai/baseline.json')
            else:
                 os.remove('.green-ai/baseline.json.bak')

@baseline.command('update')
@click.argument('path', type=click.Path(exists=True))
@click.option('--language', default='python', help='Language to scan')
def baseline_update(path, language):
    """Re-scan and update the baseline with the current state"""
    baseline_create.callback(path, language)
