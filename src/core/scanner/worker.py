from typing import Dict, Any, List
import ast
from src.core.remediation.engine import RemediationEngine
from src.core.analyzer import EmissionAnalyzer
from src.core.detectors import detect_violations

def scan_file_worker(file_path: str, language: str, config: Dict, rules: List[Dict]) -> Dict[str, Any]:
    """
    Worker function to scan and analyze a single file.
    Running in a separate process.
    """
    # Initialize analyzer
    analyzer = EmissionAnalyzer()
    remediation_engine = RemediationEngine()

    issues = []
    emissions = 0.0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Explicitly check for syntax errors
        if language == 'python':
            ast.parse(content)

        # Scan for violations
        violations = detect_violations(content, file_path, language=language)

        # Convert violations to full issue format
        for violation in violations:
            # Find rule in provided rules list
            rule = next((r for r in rules if r['id'] == violation['id']), None)

            if rule:
                rule_id = rule.get('id', violation.get('id', 'unknown'))

                # Check if rule is enabled in config
                # Re-implement is_rule_enabled logic here since we don't have ConfigLoader instance
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
                        'carbon_impact': rule.get('carbon_impact', 0.000000001),
                        'energy_factor': rule.get('energy_factor', 1),
                        'name': rule.get('name', rule_id)
                    }
                    issues.append(issue)

        # Analyze emissions
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
