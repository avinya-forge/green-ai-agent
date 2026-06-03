import pytest
import ast
from src.core.quality.dead_code import DeadCodeDetector

def test_dead_code_basic():
    code = """
def used_func():
    return 1

def unused_func():
    return 2

class UsedClass:
    pass

class UnusedClass:
    pass

used_func()
x = UsedClass()
"""
    tree = ast.parse(code)
    detector = DeadCodeDetector()
    detector.visit(tree)
    dead = detector.get_dead_code()

    dead_ids = [d['id'] for d in dead]
    dead_names = [d['name'] for d in dead]

    assert 'unused_func' in dead_names
    assert 'UnusedClass' in dead_names
    assert 'used_func' not in dead_names
    assert 'UsedClass' not in dead_names

def test_dead_code_no_dead():
    code = "def main(): pass\nmain()"
    tree = ast.parse(code)
    detector = DeadCodeDetector()
    detector.visit(tree)
    assert len(detector.get_dead_code()) == 0
