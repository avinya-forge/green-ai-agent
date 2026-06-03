"""
ESG Scoring Engine for Green AI.
Calculates a weighted aggregate score across Environmental, Security, and Governance pillars.
"""

from typing import Dict, List, Any


class ESGScorer:
    """
    Weighted ESG scoring engine.
    Weights: 40% Environmental (E), 30% Security (S), 30% Governance (G).
    """

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            'environmental': 0.4,
            'security': 0.3,
            'governance': 0.3
        }

    def calculate_score(self, e_metrics: Dict, s_metrics: Dict, g_metrics: Dict) -> float:
        """
        Calculate overall ESG score (0-100).
        """
        e_score = self._normalize_e(e_metrics)
        s_score = self._normalize_s(s_metrics)
        g_score = self._normalize_g(g_metrics)

        total = (
            e_score * self.weights['environmental'] +
            s_score * self.weights['security'] +
            g_score * self.weights['governance']
        )
        return round(total, 2)

    def _normalize_e(self, metrics: Dict) -> float:
        """Normalize Environmental score (focus on emissions and complexity)."""
        score = 100.0
        emissions = metrics.get('emissions', 0.0)
        complexity = metrics.get('cognitive_complexity', 0)

        # Heuristic deductions
        score -= min(30, emissions * 1000000)
        score -= min(40, (complexity / 100) * 40)

        return max(0.0, score)

    def _normalize_s(self, metrics: Dict) -> float:
        """Normalize Security score (focus on SAST violations)."""
        score = 100.0
        critical = metrics.get('critical', 0)
        high = metrics.get('high', 0)
        medium = metrics.get('medium', 0)

        score -= critical * 25
        score -= high * 10
        score -= medium * 5

        return max(0.0, score)

    def _normalize_g(self, metrics: Dict) -> float:
        """Normalize Governance score (focus on duplication and quality)."""
        score = 100.0
        duplication_ratio = metrics.get('duplication_ratio', 0.0)
        tech_debt_minutes = metrics.get('tech_debt_minutes', 0)

        score -= duplication_ratio * 50
        score -= min(50, (tech_debt_minutes / 480) * 50)

        return max(0.0, score)
