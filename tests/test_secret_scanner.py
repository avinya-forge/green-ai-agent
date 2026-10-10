import pytest
from src.core.security.secret_scanner import SecretScanner

def test_secret_scanner_aws():
    scanner = SecretScanner()
    content = 'aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"\naws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"'
    violations = scanner.scan(content)

    assert len(violations) == 2
    assert any(v['id'] == 'secret_aws_access_key' for v in violations)
    assert any(v['id'] == 'secret_aws_secret_key' for v in violations)

def test_secret_scanner_github():
    scanner = SecretScanner()
    content = 'const token = "ghp_123456789012345678901234567890123456";'
    violations = scanner.scan(content)

    assert any(v['id'] == 'secret_github_token' for v in violations)

def test_secret_scanner_jwt():
    scanner = SecretScanner()
    content = 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI.eyJzdWIiOiIxMjM0NTY3ODkwIiwibm.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
    violations = scanner.scan(content)

    assert len(violations) == 1
    assert violations[0]['id'] == 'secret_jwt_token'

def test_secret_scanner_generic():
    scanner = SecretScanner()
    # High entropy string
    content = 'password = "H$8d2&pK9!xLpZ1#vQ0m"'
    violations = scanner.scan(content)

    assert len(violations) > 0
    assert any(v['id'] == 'secret_generic_password_assignment' for v in violations)
