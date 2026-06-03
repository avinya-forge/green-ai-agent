import pytest
from src.core.esg.scorer import ESGScorer

def test_esg_scorer_perfect_score():
    scorer = ESGScorer()
    e = {'emissions': 0, 'cognitive_complexity': 0}
    s = {'critical': 0, 'high': 0, 'medium': 0}
    g = {'duplication_ratio': 0, 'tech_debt_minutes': 0}

    score = scorer.calculate_score(e, s, g)
    assert score == 100.0

def test_esg_scorer_deductions():
    scorer = ESGScorer()
    e = {'emissions': 0.00001, 'cognitive_complexity': 50} # e_score: 100 - 10 - 20 = 70
    s = {'critical': 1, 'high': 1, 'medium': 1}           # s_score: 100 - 25 - 10 - 5 = 60
    g = {'duplication_ratio': 0.2, 'tech_debt_minutes': 120} # g_score: 100 - 10 - 12.5 = 77.5

    # expected = 70 * 0.4 + 60 * 0.3 + 77.5 * 0.3
    # expected = 28 + 18 + 23.25 = 69.25

    score = scorer.calculate_score(e, s, g)
    assert score == 69.25

def test_esg_scorer_min_score():
    scorer = ESGScorer()
    e = {'emissions': 1.0, 'cognitive_complexity': 1000}
    s = {'critical': 10, 'high': 10, 'medium': 10}
    g = {'duplication_ratio': 1.0, 'tech_debt_minutes': 10000}

    score = scorer.calculate_score(e, s, g)
    assert score == 12.0 # E=30, S=0, G=0. Total = 30*0.4 = 12.
