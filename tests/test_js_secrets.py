import pytest
from src.core.detectors.javascript_detector import JavaScriptASTDetector

class TestJSSecrets:

    def test_hardcoded_secret_const(self):
        code = """
        const myPassword = "superSecretPassword123";
        """
        detector = JavaScriptASTDetector(code, "test.js")
        violations = detector.detect_all()

        secrets = [v for v in violations if v['id'] == 'hardcoded_secret']
        assert len(secrets) == 1
        assert secrets[0]['line'] == 2
        assert 'myPassword' in secrets[0]['message']

    def test_hardcoded_secret_let(self):
        code = """
        let apiKey = 'AKIA1234567890ABCDEF';
        """
        detector = JavaScriptASTDetector(code, "test.js")
        violations = detector.detect_all()

        secrets = [v for v in violations if v['id'] == 'hardcoded_secret']
        assert len(secrets) == 1
        assert 'apiKey' in secrets[0]['message']

    def test_hardcoded_secret_object(self):
        code = """
        const config = {
            dbPassword: "anotherSecretPassword",
            host: "localhost"
        };
        """
        detector = JavaScriptASTDetector(code, "test.js")
        violations = detector.detect_all()

        secrets = [v for v in violations if v['id'] == 'hardcoded_secret']
        assert len(secrets) == 1
        assert 'dbPassword' in secrets[0]['message']

    def test_ignored_secrets(self):
        code = """
        const password = process.env.PASSWORD; // Not a string literal
        const shortKey = "123"; // Too short
        const placeholder = "<PASSWORD>"; // Placeholder
        const envRef = "process.env.API_KEY"; // Environment reference string
        """
        detector = JavaScriptASTDetector(code, "test.js")
        violations = detector.detect_all()

        secrets = [v for v in violations if v['id'] == 'hardcoded_secret']
        assert len(secrets) == 0
