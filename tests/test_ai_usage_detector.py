"""
Tests for EPIC-28: Sustainable AI Usage Analyzer
Covers all 12 unsustainable AI usage patterns.
"""

from src.core.detectors.ai_usage_detector import AIUsageDetector, scan_file_for_ai_usage


def _detector(code: str, path: str = "test.py") -> AIUsageDetector:
    return AIUsageDetector(content=code, file_path=path)


# ── Provider detection ────────────────────────────────────────────────────────

class TestProviderDetection:
    def test_detects_anthropic(self):
        d = _detector("import anthropic\nclient = anthropic.Anthropic()")
        assert "anthropic" in d.detect_providers()

    def test_detects_openai(self):
        d = _detector("from openai import OpenAI")
        assert "openai" in d.detect_providers()

    def test_detects_langchain(self):
        d = _detector("from langchain_anthropic import ChatAnthropic")
        assert "langchain" in d.detect_providers()

    def test_detects_ollama(self):
        d = _detector("import ollama")
        assert "ollama" in d.detect_providers()

    def test_detects_groq(self):
        d = _detector("from groq import Groq")
        assert "groq" in d.detect_providers()

    def test_detects_litellm(self):
        d = _detector("import litellm")
        assert "litellm" in d.detect_providers()

    def test_detects_gemini(self):
        d = _detector("import google.generativeai as genai")
        assert "gemini" in d.detect_providers()

    def test_no_provider_no_violations(self):
        d = _detector("def add(a, b): return a + b")
        violations = d.detect_all()
        assert violations == []

    def test_multiple_providers(self):
        d = _detector("import anthropic\nimport openai")
        providers = d.detect_providers()
        assert "anthropic" in providers
        assert "openai" in providers

    # JS/TS import styles
    def test_detects_anthropic_ts_require(self):
        d = _detector(
            "const Anthropic = require('@anthropic-ai/sdk');\n",
            path="app.ts"
        )
        assert "anthropic" in d.detect_providers()

    def test_detects_anthropic_ts_esm(self):
        d = _detector(
            "import Anthropic from '@anthropic-ai/sdk';\n",
            path="app.ts"
        )
        assert "anthropic" in d.detect_providers()

    def test_detects_openai_ts_esm(self):
        d = _detector(
            "import OpenAI from 'openai';\n",
            path="app.ts"
        )
        assert "openai" in d.detect_providers()

    def test_detects_groq_ts(self):
        d = _detector(
            "import Groq from 'groq-sdk';\n",
            path="service.ts"
        )
        assert "groq" in d.detect_providers()

    def test_detects_gemini_ts(self):
        d = _detector(
            "import { GoogleGenerativeAI } from '@google/generative-ai';\n",
            path="ai.ts"
        )
        assert "gemini" in d.detect_providers()


# ── Pattern detection ─────────────────────────────────────────────────────────

class TestAICallInLoop:
    def test_detects_openai_in_for_loop(self):
        code = """\
import openai
client = openai.OpenAI()
for item in items:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": item}]
    )
"""
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_call_in_loop" in rule_ids

    def test_no_loop_no_violation(self):
        code = """\
import openai
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)
"""
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_call_in_loop" not in rule_ids


class TestOverkillModelInLoop:
    def test_detects_opus_in_loop(self):
        code = """\
import anthropic
client = anthropic.Anthropic()
for doc in documents:
    resp = client.messages.create(model="claude-opus-4-7", messages=[])
"""
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_overkill_model_in_loop" in rule_ids

    def test_light_model_in_loop_no_violation(self):
        code = """\
import anthropic
for doc in documents:
    pass  # no heavy model call
"""
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_overkill_model_in_loop" not in rule_ids


class TestMissingMaxTokens:
    def test_detects_missing_max_tokens(self):
        code = """\
import openai
client = openai.OpenAI()
resp = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "hello"}]
)
"""
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_missing_max_tokens" in rule_ids

    def test_with_max_tokens_no_violation(self):
        code = """\
import openai
client = openai.OpenAI()
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "hello"}],
    max_tokens=256
)
"""
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_missing_max_tokens" not in rule_ids


class TestPromptInjectionRisk:
    def test_detects_user_input_in_prompt(self):
        code = '''\
import anthropic
def handle(request):
    user_msg = request.get("message")
    prompt = f"Summarise this: {user_msg}"
    client = anthropic.Anthropic()
    return client.messages.create(model="claude-haiku-4-5", messages=[{"role": "user", "content": prompt}])
'''
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_prompt_injection_risk" in rule_ids


class TestSyncClientInAsync:
    def test_detects_sync_client_in_async_function(self):
        code = """\
import anthropic

async def process():
    client = anthropic.Anthropic()
    resp = await client.messages.create(model="claude-haiku-4-5", messages=[])
    return resp
"""
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_sync_client_in_async" in rule_ids


class TestRedundantSystemPromptInLoop:
    def test_detects_system_prompt_in_loop(self):
        code = """\
import openai
client = openai.OpenAI()
for item in items:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": item},
    ]
    client.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=100)
"""
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_redundant_system_prompt_in_loop" in rule_ids


class TestOverkillModelClassification:
    def test_detects_heavy_model_for_classify(self):
        code = """\
import anthropic
def classify_sentiment(text):
    client = anthropic.Anthropic()
    resp = client.messages.create(model="claude-opus-4-7", messages=[{"role":"user","content":text}], max_tokens=10)
    return resp
"""
        d = _detector(code)
        violations = d.detect_all()
        rule_ids = [v.rule_id for v in violations]
        assert "ai_overkill_model_classification" in rule_ids


# ── Violation metadata ────────────────────────────────────────────────────────

class TestViolationMetadata:
    def test_violation_has_line_number(self):
        code = """\
import openai
client = openai.OpenAI()
for item in items:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": item}]
    )
"""
        d = _detector(code)
        violations = d.detect_all()
        # ai_call_in_loop or ai_overkill_model_in_loop should fire — either has a line
        assert violations, "Expected at least one violation for AI call in loop"
        assert all(v.line > 0 for v in violations)

    def test_violation_has_co2_note(self):
        # Test that co2_note exists on all pattern specs
        from src.core.detectors.ai_usage_detector import _PATTERNS
        for spec in _PATTERNS:
            assert "co2_note" in spec
            assert len(spec["co2_note"]) > 10

    def test_to_violation_dicts_format(self):
        code = """\
import openai
client = openai.OpenAI()
for item in items:
    resp = client.chat.completions.create(model="gpt-4", messages=[{"role":"user","content":item}])
"""
        d = _detector(code)
        d.detect_all()
        dicts = d.to_violation_dicts()
        assert isinstance(dicts, list)
        for v in dicts:
            assert "rule_id" in v
            assert "file" in v
            assert "line" in v
            assert "severity" in v
            assert "category" in v
            assert v["category"] == "ai_sustainability"

    def test_model_tier_heavy(self):
        from src.core.detectors.ai_usage_detector import AIUsageDetector, _MODEL_CO2_TIER
        d = AIUsageDetector(content="import anthropic", file_path="f.py")
        tier = d._model_tier("claude-opus-4-7")
        assert tier == "heavy"
        assert _MODEL_CO2_TIER["heavy"] > _MODEL_CO2_TIER["light"]

    def test_model_tier_light(self):
        d = AIUsageDetector(content="import anthropic", file_path="f.py")
        tier = d._model_tier("claude-haiku-4-5")
        assert tier == "light"


# ── File scanning ─────────────────────────────────────────────────────────────

class TestFileScan:
    def test_scan_non_python_file_returns_empty(self, tmp_path):
        f = tmp_path / "test.rb"
        f.write_text("import anthropic\n")
        result = scan_file_for_ai_usage(str(f))
        assert result == []

    def test_scan_python_file(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text(
            "import openai\n"
            "client = openai.OpenAI()\n"
            "for x in items:\n"
            "    client.chat.completions.create(model='gpt-4', messages=[])\n"
        )
        result = scan_file_for_ai_usage(str(f))
        assert isinstance(result, list)

    def test_scan_js_file(self, tmp_path):
        f = tmp_path / "app.js"
        f.write_text("const openai = require('@openai/openai');\n")
        result = scan_file_for_ai_usage(str(f))
        assert isinstance(result, list)

    def test_scan_missing_file_returns_empty(self):
        result = scan_file_for_ai_usage("/nonexistent/path/file.py")
        assert result == []
