import pytest
import textwrap
from src.core.remediation.strategies.python import (
    ListAppendToComprehension,
    EnumerateTransformer,
    UnnecessaryComprehensionTransformer
)

class TestListAppendToComprehension:
    def test_basic_append_loop(self):
        strategy = ListAppendToComprehension()
        code = textwrap.dedent("""
        items = [1, 2, 3]
        results = []
        for x in items:
            results.append(x * 2)
        """)

        # Line 4 is the 'for' loop
        diff = strategy.get_diff("test.py", code, 4)
        assert diff is not None
        assert "results.extend([x * 2 for x in items])" in diff

    def test_no_change_if_complex_body(self):
        strategy = ListAppendToComprehension()
        code = textwrap.dedent("""
        items = [1, 2, 3]
        results = []
        for x in items:
            y = x * 2
            results.append(y)
        """)

        diff = strategy.get_diff("test.py", code, 4)
        assert diff is None

class TestEnumerateTransformer:
    def test_range_len_usage(self):
        strategy = EnumerateTransformer()
        code = textwrap.dedent("""
        items = ['a', 'b', 'c']
        for i in range(len(items)):
            print(items[i])
        """)

        diff = strategy.get_diff("test.py", code, 3)
        assert diff is not None
        assert "enumerate(items)" in diff

class TestUnnecessaryComprehensionTransformer:
    def test_list_comprehension(self):
        strategy = UnnecessaryComprehensionTransformer()
        code = textwrap.dedent("""
        items = [1, 2, 3]
        new_list = list([x for x in items])
        """)

        diff = strategy.get_diff("test.py", code, 3)
        assert diff is not None
        assert "new_list = list(items)" in diff

    def test_set_comprehension(self):
        strategy = UnnecessaryComprehensionTransformer()
        code = textwrap.dedent("""
        items = [1, 2, 3]
        new_set = set({x for x in items})
        """)

        diff = strategy.get_diff("test.py", code, 3)
        assert diff is not None
        assert "new_set = set(items)" in diff

    def test_safe_comprehension_with_filter(self):
        strategy = UnnecessaryComprehensionTransformer()
        code = textwrap.dedent("""
        items = [1, 2, 3]
        new_list = list([x for x in items if x > 0])
        """)

        diff = strategy.get_diff("test.py", code, 3)
        assert diff is None

    def test_safe_comprehension_with_transformation(self):
        strategy = UnnecessaryComprehensionTransformer()
        code = textwrap.dedent("""
        items = [1, 2, 3]
        new_list = list([x * 2 for x in items])
        """)

        diff = strategy.get_diff("test.py", code, 3)
        assert diff is None
