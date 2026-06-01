from typing import Dict, Any, List
import ast
from src.core.remediation.engine import RemediationEngine
from src.core.analyzer import EmissionAnalyzer
from src.core.detectors import detect_violations
from src.core.detectors.ai_usage_detector import scan_file_for_ai_usage
from src.core.cache import DiskCache
from src.core.scanner.suppression import get_suppressions, is_suppressed, load_external_suppressions
import os

_disk_cache_instance = None

def _checks_include(config: Dict, check: str) -> bool:
    checks = config.get('checks', ['all'])
    if isinstance(checks, str):
        checks = [checks]
    return 'all' in checks or check in checks

def scan_file_worker(
    file_path: str, language: str, config: Dict, rules: List[Dict]
) -> Dict[str, Any]:
    global _disk_cache_instance

    try:
        analyzer = EmissionAnalyzer()
        remediation_engine = RemediationEngine()

        cache_config = config.get('cache', {})
        cache_enabled = cache_config.get('enabled', True)
        cache_path = cache_config.get('path', '.green-ai/cache')

        disk_cache = None
        if cache_enabled:
            expanded_path = os.path.expanduser(cache_path)
            if _disk_cache_instance is None or _disk_cache_instance.cache_dir != expanded_path:
                _disk_cache_instance = DiskCache(cache_dir=cache_path)
            disk_cache = _disk_cache_instance

        # Load suppressions fresh per file to avoid global state issues in tests
        external_suppressions = load_external_suppressions()

        issues = []
        emissions = 0.0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            inline_suppressions = get_suppressions(content)

            if language == 'python':
                try:
                    ast.parse(content)
                except SyntaxError:
                    pass # Handled below

            violations = None
            if disk_cache:
                violations = disk_cache.get(content, language)

            if violations is None:
                violations = detect_violations(content, file_path, language=language)
                if disk_cache:
                    disk_cache.set(content, language, violations)

            for violation in violations:
                rule = next((r for r in rules if r['id'] == violation['id']), None)
                if rule:
                    rule_id = rule.get('id', violation.get('id', 'unknown'))
                    enabled_rules = config.get('rules', {}).get('enabled', [])
                    disabled_rules = config.get('rules', {}).get('disabled', [])

                    is_enabled = True
                    if rule_id in disabled_rules:
                        is_enabled = False
                    elif rule_id in enabled_rules:
                        is_enabled = True

                    if is_enabled:
                        issue = {
                            'id': rule_id,
                            'type': 'green_violation',
                            'severity': rule.get('severity', 'medium'),
                            'message': violation.get('message', 'N/A'),
                            'file': file_path,
                            'line': violation.get('line', 0),
                            'remediation': rule.get('remediation', 'N/A'),
                            'ai_suggestion': remediation_engine.get_suggestion(rule_id),
                            'effort': rule.get('effort', 'Medium'),
                            'tags': rule.get('tags', []),
                            'carbon_impact': rule.get('carbon_impact', 1e-9),
                            'energy_factor': rule.get('energy_factor', 1),
                            'name': rule.get('name', rule_id)
                        }

                        if not is_suppressed(issue, inline_suppressions, external_suppressions):
                            issues.append(issue)

            if _checks_include(config, 'ai'):
                ai_violations = scan_file_for_ai_usage(file_path)
                for av in ai_violations:
                    rule_id = av['rule_id']
                    issue = {
                        'id': rule_id,
                        'type': 'ai_sustainability',
                        'severity': av['severity'],
                        'message': av['message'],
                        'file': av['file'],
                        'line': av['line'],
                        'remediation': av.get('co2_note', ''),
                        'ai_suggestion': None,
                        'effort': 'Medium',
                        'tags': ['ai', 'sustainability', av.get('provider', 'ai')],
                        'carbon_impact': av.get('estimated_co2_g', 0) * 1e-6,
                        'energy_factor': 1,
                        'name': rule_id.replace('_', ' ').title(),
                        'category': 'ai_sustainability',
                        'co2_note': av.get('co2_note', ''),
                        'provider': av.get('provider'),
                        'model_tier': av.get('model_tier', 'unknown'),
                        'estimated_co2_g': av.get('estimated_co2_g', 0),
                    }
                    if not is_suppressed(issue, inline_suppressions, external_suppressions):
                        issues.append(issue)

            metrics = analyzer.analyze_file(file_path, content)
            emissions = analyzer.estimate_emissions(metrics)

        except SyntaxError:
            issues.append({
                'id': 'syntax_error',
                'type': 'error',
                'severity': 'blocker',
                'message': f'Syntax error in {language} code',
                'file': file_path,
                'line': 0,
                'remediation': 'Fix the syntax error to proceed with scanning.',
                'effort': 'Low',
                'tags': ['syntax', 'error']
            })
        except Exception as e:
            issues.append({
                'id': 'parse_error',
                'type': 'error',
                'severity': 'medium',
                'message': f'Failed to scan file: {str(e)}',
                'file': file_path,
                'line': 0,
                'remediation': 'Check file content and format.',
                'effort': 'Low',
                'tags': ['error']
            })

        return {
            'issues': issues,
            'emissions': emissions
        }
    except Exception as e:
        return {
            'issues': [{
                'id': 'worker_crash',
                'type': 'error',
                'severity': 'critical',
                'message': f'Worker process crashed: {str(e)}',
                'file': file_path,
                'line': 0,
                'remediation': 'Report this bug to the maintainers.',
                'effort': 'Low',
                'tags': ['error', 'crash']
            }],
            'emissions': 0.0
        }
