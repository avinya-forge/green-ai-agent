from src.core.scanner import Scanner
import os


def test_python_security_expansion():
    scanner = Scanner(language='python')
    code = """
import hashlib
import yaml

# Insecure Hash
h = hashlib.md5(b'password')

# Unsafe YAML
data = yaml.load("user: input")

# Binding to all
host = '0.0.0.0'
"""
    with open("test_sec_py.py", "w") as f:
        f.write(code)

    try:
        results = scanner.scan("test_sec_py.py")
        issue_ids = [i['id'] for i in results['issues']]

        # Checking if rules are in backlog/repository first
        from src.core.rules import RuleRepository
        repo = RuleRepository()
        python_rules = repo.get_rules('python')
        python_ids = [r['id'] for r in python_rules]

        assert 'insecure_hash' in python_ids
        assert 'unsafe_yaml_load' in python_ids
        assert 'bind_all_interfaces' in python_ids

        # Now check if detected
        assert 'insecure_hash' in issue_ids
        assert 'unsafe_yaml_load' in issue_ids
        assert 'bind_all_interfaces' in issue_ids
    finally:
        if os.path.exists("test_sec_py.py"):
            os.remove("test_sec_py.py")
