class ESGScoreEngine:
    """Computes aggregate ESG scores using a weighted algorithm."""

    ENVIRONMENTAL_WEIGHT = 0.4
    SECURITY_WEIGHT = 0.3
    GOVERNANCE_WEIGHT = 0.3

    @classmethod
    def compute_aggregate_score(cls, environmental_score: float, security_score: float, governance_score: float) -> float:
        """
        Calculate weighted aggregate score.
        Weights: 40% E, 30% S, 30% G

        Args:
            environmental_score: 0-100
            security_score: 0-100
            governance_score: 0-100

        Returns:
            Weighted aggregate score from 0-100, rounded to 2 decimal places.
        """
        score = (
            (environmental_score * cls.ENVIRONMENTAL_WEIGHT) +
            (security_score * cls.SECURITY_WEIGHT) +
            (governance_score * cls.GOVERNANCE_WEIGHT)
        )
        return round(score, 2)
