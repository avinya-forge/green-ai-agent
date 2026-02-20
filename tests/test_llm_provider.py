import unittest
from unittest.mock import patch, MagicMock
from src.core.llm.openai_provider import OpenAIProvider
from src.core.llm.mock_provider import MockLLMProvider
from src.core.llm.factory import LLMFactory

class TestOpenAIProvider(unittest.TestCase):

    def setUp(self):
        self.api_key = "sk-test-key"
        self.provider = OpenAIProvider(self.api_key)

    @patch('src.core.llm.openai_provider.requests.post')
    def test_generate_fix_success(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Here is the fix:\n```python\ncorrected_code()\n```"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        code_snippet = "bad_code()"
        violation_description = "Inefficient code"
        fix = self.provider.generate_fix(code_snippet, violation_description)

        self.assertEqual(fix, "corrected_code()")
        mock_post.assert_called_once()

    @patch('src.core.llm.openai_provider.requests.post')
    def test_api_failure(self, mock_post):
        # Mock API failure
        import requests
        mock_post.side_effect = requests.RequestException("API Error")

        fix = self.provider.generate_fix("code", "violation")
        self.assertIsNone(fix)

class TestMockLLMProvider(unittest.TestCase):
    def test_mock_defaults(self):
        provider = MockLLMProvider()
        self.assertIn("Mock fix applied", provider.generate_fix("code", "desc"))
        self.assertIn("Mock explanation", provider.explain_violation("code", "desc"))
        self.assertEqual(provider.estimate_cost(10, 10), 0.0)

    def test_mock_custom_responses(self):
        responses = {
            "fix": "custom fix",
            "explanation": "custom explanation",
            "cost": 0.5
        }
        provider = MockLLMProvider(responses=responses)
        self.assertEqual(provider.generate_fix("code", "desc"), "custom fix")
        self.assertEqual(provider.explain_violation("code", "desc"), "custom explanation")
        self.assertEqual(provider.estimate_cost(10, 10), 0.5)

class TestLLMFactory(unittest.TestCase):

    @patch('os.getenv')
    def test_get_openai_provider(self, mock_getenv):
        mock_getenv.return_value = "sk-env-key"
        provider = LLMFactory.get_provider("openai")
        self.assertIsInstance(provider, OpenAIProvider)
        self.assertEqual(provider.api_key, "sk-env-key")

    @patch('os.getenv')
    def test_missing_key(self, mock_getenv):
        mock_getenv.return_value = None
        provider = LLMFactory.get_provider("openai")
        self.assertIsNone(provider)

    def test_unknown_provider(self):
        provider = LLMFactory.get_provider("unknown")
        self.assertIsNone(provider)

    def test_get_mock_provider(self):
        provider = LLMFactory.get_provider("mock")
        self.assertIsInstance(provider, MockLLMProvider)
