"""
Tests for dictionary utilities.
"""

from src.utils.dict_utils import deep_merge

def test_deep_merge_simple():
    base = {'a': 1, 'b': 2}
    override = {'b': 3, 'c': 4}
    result = deep_merge(base, override)

    assert result['a'] == 1
    assert result['b'] == 3
    assert result['c'] == 4

def test_deep_merge_nested():
    base = {
        'a': 1,
        'nested': {
            'x': 10,
            'y': 20
        }
    }
    override = {
        'nested': {
            'y': 25,
            'z': 30
        }
    }
    result = deep_merge(base, override)

    assert result['a'] == 1
    assert result['nested']['x'] == 10
    assert result['nested']['y'] == 25
    assert result['nested']['z'] == 30

def test_deep_merge_type_mismatch():
    """Test replacing a dict with a non-dict and vice versa."""
    base = {'a': {'x': 1}}
    override = {'a': 5}
    result = deep_merge(base, override)
    assert result['a'] == 5

    base2 = {'a': 5}
    override2 = {'a': {'x': 1}}
    result2 = deep_merge(base2, override2)
    assert result2['a'] == {'x': 1}

def test_deep_merge_lists():
    """Lists should be overwritten, not merged (standard behavior for simple merge)."""
    base = {'items': [1, 2]}
    override = {'items': [3, 4]}
    result = deep_merge(base, override)
    assert result['items'] == [3, 4]

def test_deep_merge_no_mutation():
    """Ensure original dicts are not modified."""
    base = {'a': {'x': 1}}
    override = {'a': {'y': 2}}
    deep_merge(base, override)

    assert base['a'] == {'x': 1}
    assert override['a'] == {'y': 2}
