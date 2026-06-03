# runtime_monitor/main.py
"""
Main entry point for runtime monitoring in Green-AI.
"""

from typing import List, Dict, Any
from .data_collector import RuntimeDataCollector
from .pattern_analyzer import PatternAnalyzer
from .remediation_suggester import RemediationSuggester


class RuntimeMonitor:
    """Monitor and analyze runtime execution of code."""

    def __init__(self):
        self.collector = RuntimeDataCollector()
        self.analyzer = PatternAnalyzer()
        self.suggester = RemediationSuggester()

    def monitor_execution(self, command: List[str]) -> Dict[str, Any]:
        """Run a command and monitor its resource usage."""
        # This is a simplified version for the core scanner integration
        # Real implementation would call data_collector.collect_data
        report = self.collector.collect_from_command(command)
        patterns = self.analyzer.analyze([report])
        remediations = self.suggester.suggest(patterns)

        return {
            "report": report,
            "patterns": patterns,
            "remediations": remediations
        }


def run_runtime_analysis(code_snippet, language="python", iterations=1):
    """Run full runtime analysis pipeline."""
    collector = RuntimeDataCollector(language)
    reports = collector.collect_data(code_snippet, iterations)
    analyzer = PatternAnalyzer()
    patterns = analyzer.analyze(reports)
    suggester = RemediationSuggester()
    remediations = suggester.suggest(patterns)
    return {
        "reports": reports,
        "patterns": patterns,
        "remediations": remediations
    }
