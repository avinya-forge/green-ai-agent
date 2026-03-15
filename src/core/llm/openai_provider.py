from typing import Optional
from .provider import LLMProvider
import requests
import json
from src.utils.logger import logger
from src.core.llm.prompts import PromptManager


class OpenAIProvider(LLMProvider):
    """
    OpenAI-based LLM provider.
    """

    DEFAULT_MODEL = "gpt-4o"
    API_URL = "https://api.openai.com/v1/chat/completions"

    # Cost per 1K tokens (approx, as of late 2024/early 2025)
    COSTS = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_fix(self, code_snippet: str, violation_description: str, language: str = "python") -> Optional[str]:
        """
        Generate a fix using OpenAI Chat Completion.
        """
        system_prompt = PromptManager.get_system_prompt()
        user_prompt = PromptManager.get_fix_prompt(language, violation_description, code_snippet)

        return self._query_openai(system_prompt, user_prompt)

    def explain_violation(self, code_snippet: str, violation_description: str, language: str = "python") -> Optional[str]:
        """
        Explain the violation.
        """
        system_prompt = (
            "You are a helpful assistant explaining software inefficiencies. "
            "Focus on energy consumption and performance impact."
        )

        user_prompt = (
            f"Explain why this {language} code is inefficient:\n"
            f"Violation: {violation_description}\n\n"
            f"Code:\n```\n{code_snippet}\n```"
        )

        return self._query_openai(system_prompt, user_prompt)

    def _query_openai(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        # Apply rate limiting if configured
        if self.rate_limiter:
            # Estimate tokens: prompt length / 4 (heuristic)
            estimated_tokens = (len(system_prompt) + len(user_prompt)) // 4
            self.rate_limiter.wait_for(estimated_tokens)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }

        try:
            response = requests.post(self.API_URL, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'usage' in data:
                usage = data['usage']
                self.track_usage(
                    prompt_tokens=usage.get('prompt_tokens', 0),
                    completion_tokens=usage.get('completion_tokens', 0)
                )

            content = data['choices'][0]['message']['content']

            # Simple extraction of code block if present
            if "```" in content:
                # Try to extract content between first ``` and last ```
                parts = content.split("```")
                if len(parts) >= 3:
                    # parts[1] is typically the code (maybe with language hint)
                    code_block = parts[1]
                    if "\n" in code_block:
                        # Remove language hint (e.g., 'python\n')
                        code_block = code_block.split("\n", 1)[1]
                    return code_block.strip()

            return content.strip()

        except requests.RequestException as e:
            logger.error(f"OpenAI API request failed: {e}")
            return None
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return None

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate cost based on model pricing.
        """
        model_costs = self.COSTS.get(self.model, self.COSTS["gpt-4o"])
        input_cost = (prompt_tokens / 1000) * model_costs["input"]
        output_cost = (completion_tokens / 1000) * model_costs["output"]
        return input_cost + output_cost
