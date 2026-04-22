"""
Sustainable AI Usage Analyzer (EPIC-28)

Detects AI/LLM SDK imports and flags unsustainable usage patterns across
all major providers: Anthropic, OpenAI, LangChain, Ollama, Bedrock,
Vertex, Groq, Mistral, Cohere, LlamaIndex, LiteLLM.

Detection is text/regex-based (not AST) because AI SDK call patterns
span many import styles and are better caught via pattern matching.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional


# CO2 estimate (gCO2e per 1k tokens) by model tier — from public benchmarks
_MODEL_CO2_TIER: Dict[str, float] = {
    "heavy": 10.0,   # claude-opus-*, gpt-4*, o1-*, o3-*, gemini-ultra
    "medium": 2.0,   # claude-sonnet-*, gpt-3.5-*, gemini-pro, mistral-medium
    "light": 0.3,    # claude-haiku-*, gpt-4o-mini, gemini-flash, ollama (local)
    "unknown": 1.0,
}

_HEAVY_MODELS = re.compile(
    r"claude-opus|gpt-4[^o]|gpt-4$|o1-|o3-|gemini-ultra|mistral-large"
    r"|command-r-plus",
    re.IGNORECASE,
)
_LIGHT_MODELS = re.compile(
    r"claude-haiku|gpt-4o-mini|gpt-3\.5|gemini-flash|gemini-nano"
    r"|mistral-tiny|llama|phi-|qwen|ollama",
    re.IGNORECASE,
)

# Provider import signatures → provider name
_PROVIDER_IMPORTS: List[tuple] = [
    (re.compile(r"\bimport\s+anthropic\b|from\s+anthropic\b"), "anthropic"),
    (re.compile(r"\bimport\s+openai\b|from\s+openai\b"), "openai"),
    (re.compile(r"\bfrom\s+langchain\b|from\s+langchain_"), "langchain"),
    (re.compile(r"\bimport\s+ollama\b|from\s+ollama\b"), "ollama"),
    (re.compile(r"\bboto3\b.*bedrock|bedrock.*\bboto3\b|bedrock-runtime"), "bedrock"),
    (re.compile(r"\bvertexai\b|from\s+google\.cloud\s+import\s+aiplatform"), "vertexai"),
    (re.compile(r"\bimport\s+groq\b|from\s+groq\b"), "groq"),
    (re.compile(r"\bimport\s+mistralai\b|from\s+mistralai\b"), "mistral"),
    (re.compile(r"\bimport\s+cohere\b|from\s+cohere\b"), "cohere"),
    (re.compile(r"\bfrom\s+llama_index\b|from\s+llama-index\b"), "llamaindex"),
    (re.compile(r"\bimport\s+litellm\b|from\s+litellm\b"), "litellm"),
    (re.compile(r"\bimport\s+google\.generativeai\b|from\s+google\.generativeai\b"), "gemini"),
    (re.compile(r"@anthropic-ai/sdk|@openai/openai|openai/openai"), "openai_ts"),
    (re.compile(r"@anthropic-ai/sdk"), "anthropic_ts"),
]

# Unsustainable pattern definitions
_PATTERNS: List[Dict] = [
    {
        "id": "ai_overkill_model_in_loop",
        "severity": "major",
        "message": (
            "Heavy AI model call inside a loop — use a lighter model "
            "(claude-haiku, gpt-4o-mini) for batch/loop inference."
        ),
        "co2_note": "~33x more CO2 than haiku-class models per token.",
        "regex": re.compile(
            r"(for\s.*:|while\s.*:)[^{]*?"
            r"(claude-opus|gpt-4[^o\w]|o1-preview|o3-|gemini-ultra)",
            re.DOTALL,
        ),
    },
    {
        "id": "ai_missing_max_tokens",
        "severity": "minor",
        "message": (
            "AI API call without max_tokens/max_output_tokens budget — "
            "unbounded responses waste tokens and CO2."
        ),
        "co2_note": "Uncapped responses can 10x token usage vs. a budgeted call.",
        "regex": re.compile(
            r"(messages\.create|chat\.completions\.create|generate_content"
            r"|invoke_model|chat\.complete|run\(|acall\()"
            r"(?![\s\S]{0,500}max_tokens)",
            re.DOTALL,
        ),
    },
    {
        "id": "ai_no_prompt_caching",
        "severity": "minor",
        "message": (
            "Anthropic API call without cache_control — repeated system "
            "prompts should use prompt caching to reduce token cost by up to 90%."
        ),
        "co2_note": "Cache hits skip re-processing; saves ~90% CO2 on cached tokens.",
        "regex": re.compile(
            r"anthropic.*messages\.create|client\.messages\.create"
            r"(?![\s\S]{0,800}cache_control)",
            re.DOTALL,
        ),
        "providers": ["anthropic"],
    },
    {
        "id": "ai_call_in_loop",
        "severity": "critical",
        "message": (
            "AI API call inside a loop — batch requests or use "
            "embeddings/classification instead of per-item LLM calls."
        ),
        "co2_note": "N loop iterations = N × single-call CO2; batch APIs reduce this.",
        "regex": re.compile(
            r"(?:for\s+.+?:|while\s+[^:]+:)[^\n]*\n"
            r"(?:[ \t]+[^\n]*\n){0,10}"
            r"[ \t]+(?:[^\n]*(?:messages\.create|completions\.create"
            r"|generate_content|litellm\.completion|groq\.chat))",
            re.MULTILINE,
        ),
    },
    {
        "id": "ai_pii_in_prompt",
        "severity": "critical",
        "message": (
            "Potential PII pattern concatenated into AI prompt — "
            "sanitize user data before sending to external AI APIs."
        ),
        "co2_note": "PII leakage risk; also causes inflated prompt sizes.",
        "regex": re.compile(
            r"(f['\"]|\.format\(|%\s*\()"
            r"(?=[^'\"]{0,200}"
            r"(\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b"    # SSN
            r"|\b\d{16}\b"                              # credit card
            r"|password\s*=|api_key\s*=|secret\s*=))",
            re.IGNORECASE | re.DOTALL,
        ),
    },
    {
        "id": "ai_prompt_injection_risk",
        "severity": "critical",
        "message": (
            "Unsanitized user input directly interpolated into AI prompt — "
            "validate and escape before sending to LLM."
        ),
        "co2_note": "Injection attacks can inflate token usage via adversarial prompts.",
        "regex": re.compile(
            r"(request\.(get|json|form|args)|input\(|sys\.stdin"
            r"|req\.body|req\.query|req\.params)"
            r"[\s\S]{0,200}"
            r"(f['\"][\s\S]{0,200}\{|\.format\([\s\S]{0,100}"
            r"|messages.*content.*\+)",
            re.DOTALL,
        ),
    },
    {
        "id": "ai_unvalidated_output",
        "severity": "major",
        "message": (
            "AI response used without validation or error handling — "
            "LLM outputs are non-deterministic; always validate structure."
        ),
        "co2_note": "Silent failures cause retry storms, multiplying CO2.",
        "regex": re.compile(
            r"(\.choices\[0\]\.message\.content|\.content\[0\]\.text"
            r"|response\[.text.\]|output\.text)"
            r"(?![\s\S]{0,300}(try|except|if\s|assert|validate|schema))",
            re.DOTALL,
        ),
    },
    {
        "id": "ai_sync_client_in_async",
        "severity": "major",
        "message": (
            "Synchronous AI client used inside an async function — "
            "use AsyncAnthropic/AsyncOpenAI to avoid blocking the event loop."
        ),
        "co2_note": "Blocking async context wastes idle CPU cycles.",
        "regex": re.compile(
            r"async\s+def\s+\w+[\s\S]{0,500}"
            r"(anthropic\.Anthropic\(\)|openai\.OpenAI\(\)|Groq\(\)|Cohere\(\))",
            re.DOTALL,
        ),
    },
    {
        "id": "ai_no_retry_handling",
        "severity": "minor",
        "message": (
            "AI API call without retry/backoff logic — rate limit errors "
            "cause silent failures; use tenacity or provider SDK retry params."
        ),
        "co2_note": "Unhandled rate limits cause repeat calls, wasting compute.",
        "regex": re.compile(
            r"(messages\.create|completions\.create|generate_content|invoke_model)"
            r"(?![\s\S]{0,600}(retry|backoff|tenacity|max_retries|RateLimitError))",
            re.DOTALL,
        ),
    },
    {
        "id": "ai_streaming_disabled_large_output",
        "severity": "minor",
        "message": (
            "Large max_tokens set without streaming — enable stream=True "
            "for responses >500 tokens to reduce memory pressure."
        ),
        "co2_note": "Non-streaming large responses buffer in memory, increasing GC cost.",
        "regex": re.compile(
            r"max_tokens\s*=\s*([5-9]\d{2}|[1-9]\d{3,})"
            r"(?![\s\S]{0,200}stream\s*=\s*True)",
            re.DOTALL,
        ),
    },
    {
        "id": "ai_redundant_system_prompt_in_loop",
        "severity": "major",
        "message": (
            "System prompt defined inside a loop — move static system "
            "prompts outside loops and use prompt caching."
        ),
        "co2_note": "Rebuilding identical prompts per iteration wastes tokens.",
        "regex": re.compile(
            r"(?:for\s+.+?:|while\s+[^:]+:)[^\n]*\n"
            r"(?:[ \t]+[^\n]*\n){0,15}"
            r'[ \t]+.*["\']role["\']\s*:\s*["\']system["\']',
            re.MULTILINE,
        ),
    },
    {
        "id": "ai_overkill_model_classification",
        "severity": "major",
        "message": (
            "Heavy model used for a classification/extraction task — "
            "use haiku/flash/mini-class models; they match accuracy at 10% CO2."
        ),
        "co2_note": "Heavy models are ~33x more carbon-intensive than light models.",
        "regex": re.compile(
            r"(classify|categorize|extract|label|sentiment|is_|check_)"
            r"[\s\S]{0,300}"
            r"(claude-opus|gpt-4[^o\w]|o1-|gemini-ultra)",
            re.DOTALL | re.IGNORECASE,
        ),
    },
]


@dataclass
class AIViolation:
    rule_id: str
    file_path: str
    line: int
    message: str
    severity: str
    co2_note: str
    provider: Optional[str] = None
    model_tier: str = "unknown"
    estimated_co2_per_call_g: float = 0.0


@dataclass
class AIUsageDetector:
    """
    Scans source files for AI SDK usage and flags unsustainable patterns.
    Supports Python and JavaScript/TypeScript.
    """

    content: str
    file_path: str
    violations: List[AIViolation] = field(default_factory=list)

    def detect_providers(self) -> List[str]:
        """Return list of AI provider names imported in this file."""
        found = []
        for pattern, provider in _PROVIDER_IMPORTS:
            if pattern.search(self.content):
                found.append(provider)
        return found

    def _line_of_match(self, match: re.Match) -> int:
        return self.content[: match.start()].count("\n") + 1

    def _model_tier(self, content_snippet: str) -> str:
        if _HEAVY_MODELS.search(content_snippet):
            return "heavy"
        if _LIGHT_MODELS.search(content_snippet):
            return "light"
        return "medium"

    def detect_all(self) -> List[AIViolation]:
        providers = self.detect_providers()
        if not providers:
            return []

        for spec in _PATTERNS:
            # Skip provider-specific patterns when provider not imported
            required_providers = spec.get("providers")
            if required_providers and not any(p in providers for p in required_providers):
                continue

            for match in spec["regex"].finditer(self.content):
                snippet = match.group(0)
                tier = self._model_tier(snippet)
                self.violations.append(
                    AIViolation(
                        rule_id=spec["id"],
                        file_path=self.file_path,
                        line=self._line_of_match(match),
                        message=spec["message"],
                        severity=spec["severity"],
                        co2_note=spec["co2_note"],
                        provider=providers[0] if providers else None,
                        model_tier=tier,
                        estimated_co2_per_call_g=_MODEL_CO2_TIER.get(tier, 1.0),
                    )
                )

        return self.violations

    def to_violation_dicts(self) -> List[Dict]:
        """Convert to the standard Violation dict format used by the scanner."""
        results = []
        for v in self.violations:
            results.append(
                {
                    "rule_id": v.rule_id,
                    "file": v.file_path,
                    "line": v.line,
                    "message": v.message,
                    "severity": v.severity,
                    "category": "ai_sustainability",
                    "co2_note": v.co2_note,
                    "provider": v.provider,
                    "model_tier": v.model_tier,
                    "estimated_co2_g": v.estimated_co2_per_call_g,
                }
            )
        return results


def scan_file_for_ai_usage(file_path: str) -> List[Dict]:
    """Entry point: scan a single file and return violation dicts."""
    path = Path(file_path)
    if path.suffix not in {".py", ".js", ".ts", ".tsx", ".jsx"}:
        return []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    detector = AIUsageDetector(content=content, file_path=file_path)
    detector.detect_all()
    return detector.to_violation_dicts()
