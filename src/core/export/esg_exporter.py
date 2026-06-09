from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.core.sbom.sci import SCICalculator
from src.utils.logger import logger

TEMPLATE_DIR = Path(__file__).parent / 'templates'
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / 'output'


class ESGExporter:
    """Generates ESG compliance reports"""

    def __init__(self, output_path: Optional[str] = None):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.output_path = output_path or str(OUTPUT_DIR / 'esg-report.pdf')

    def export(self, results: Dict[str, Any], project_name: str = 'Scan') -> str:
        try:
            import weasyprint
        except ImportError:
            logger.error("WeasyPrint not installed. Cannot export ESG PDF.")
            return ""

        # Calculate SCI
        sci_calc = SCICalculator()
        sci_report = sci_calc.get_sci_report(results)

        # Security metrics (mock for now based on issues)
        issues = results.get('issues', [])
        critical_count = sum(1 for i in issues if i.get('severity') == 'critical')
        security_violations = sum(1 for i in issues if 'security' in i.get('tags', []))
        secret_count = sum(1 for i in issues if 'secret' in i.get('tags', []))

        # Governance metrics
        debt_hours = len(issues) * 0.5  # Simple heuristic: 30 mins per issue

        context = {
            'project_name': project_name,
            'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            'sci_score': sci_report['sci_score'],
            'sci_unit': sci_report['unit'],
            'energy_kwh': sci_report['energy_kwh'],
            'carbon_intensity': sci_report['carbon_intensity'],
            'critical_count': critical_count,
            'security_violations': security_violations,
            'secret_count': secret_count,
            'debt_hours': debt_hours,
            'compliance_status': 'IN REVIEW' if critical_count > 0 else 'PASSED'
        }

        env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('esg_report.html')
        html_content = template.render(**context)

        weasyprint.HTML(string=html_content).write_pdf(self.output_path)
        return self.output_path
