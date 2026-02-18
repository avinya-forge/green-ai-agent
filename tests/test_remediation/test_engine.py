import pytest
from src.core.remediation.engine import RemediationEngine

class TestRemediationEngine:
    def test_load_strategies(self):
        engine = RemediationEngine()
        # Should have at least one strategy
        assert len(engine._strategies) > 0
        assert 'inefficient_loop' in engine._strategies

    def test_get_suggestion(self):
        engine = RemediationEngine()
        suggestion = engine.get_suggestion('inefficient_loop')
        assert "Convert loop" in suggestion

        # Fallback
        suggestion = engine.get_suggestion('unknown_loop')
        assert "Consider optimizing the loop" in suggestion

    def test_get_diff(self):
        engine = RemediationEngine()
        code = """
items = [1, 2]
results = []
for x in items:
    results.append(x)
"""
        diff = engine.get_diff("test.py", code, 4, 'inefficient_loop')
        assert diff is not None
        assert "extend" in diff

    def test_legacy_api(self):
        engine = RemediationEngine()
        suggestion = engine.suggest_fix({'id': 'inefficient_loop'})
        assert "Convert loop" in suggestion
