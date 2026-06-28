import pytest
from src.core.esg.score_engine import ESGScoreEngine

def test_compute_aggregate_score():
    score = ESGScoreEngine.compute_aggregate_score(100.0, 100.0, 100.0)
    assert score == 100.0

    score = ESGScoreEngine.compute_aggregate_score(0.0, 0.0, 0.0)
    assert score == 0.0

    score = ESGScoreEngine.compute_aggregate_score(50.0, 80.0, 20.0)
    # (50 * 0.4) + (80 * 0.3) + (20 * 0.3)
    # = 20 + 24 + 6 = 50.0
    assert score == 50.0

def test_compute_aggregate_score_rounding():
    score = ESGScoreEngine.compute_aggregate_score(33.33, 66.67, 12.34)
    # (33.33 * 0.4) + (66.67 * 0.3) + (12.34 * 0.3)
    # = 13.332 + 20.001 + 3.702 = 37.035 -> 37.03 or 37.04 depending on rounding.
    # Python round(37.035, 2) is 37.04
    assert score == round(37.035, 2)
