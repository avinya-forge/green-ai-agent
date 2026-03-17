from typing import Any, Dict, List, Optional
from src.standards.registry import StandardsRegistry
from src.core.project_manager import ProjectManager
from src.core.history import HistoryManager
from src.core.remediation.engine import RemediationEngine
from src.ui.charts import generate_all_charts

# Global State
last_scan_results: Optional[Dict[str, Any]] = None
last_charts: Optional[Dict[str, Any]] = None

# Singletons
standards_registry: Optional[StandardsRegistry] = None
project_manager: Optional[ProjectManager] = None
history_manager: Optional[HistoryManager] = None
remediation_engine: Optional[RemediationEngine] = None


def get_standards_registry() -> StandardsRegistry:
    global standards_registry
    if standards_registry is None:
        standards_registry = StandardsRegistry()
    return standards_registry


def get_project_manager() -> ProjectManager:
    global project_manager
    if project_manager is None:
        project_manager = ProjectManager()
    return project_manager


def get_history_manager() -> HistoryManager:
    global history_manager
    if history_manager is None:
        history_manager = HistoryManager()
    return history_manager


def get_remediation_engine() -> RemediationEngine:
    global remediation_engine
    if remediation_engine is None:
        remediation_engine = RemediationEngine()
    return remediation_engine


def set_last_scan_results(results: Dict[str, Any]):
    global last_scan_results, last_charts
    last_scan_results = results
    last_charts = generate_all_charts(results)


def generate_insights(results: Dict[str, Any]) -> List[str]:
    insights = []
    issue_count = len(results.get('issues', []))

    if issue_count > 5:
        insights.append("High number of issues detected. Consider refactoring the codebase for better green practices.")

    if any(i.get('severity') == 'high' for i in results.get('issues', [])):
        insights.append("Critical high-severity issues found. Prioritize fixing these for maximum energy savings.")

    scanning_emissions = results.get('scanning_emissions', 0)
    if scanning_emissions > 0.00001:
        insights.append("Scan process emissions are notable. Consider optimizing scanning frequency or hardware.")

    codebase_emissions = results.get('codebase_emissions', 0)
    if codebase_emissions > 0.000001:
        insights.append(f"Estimated codebase emissions are {codebase_emissions:.9f} kg CO₂. Fixing the high-severity issues will reduce this impact.")

    if codebase_emissions > scanning_emissions * 10:
        insights.append("Codebase emissions significantly exceed scanning emissions. Focus on optimizing the analyzed code.")

    return insights
