from typing import Dict, Optional

class PromptManager:
    """
    Manages LLM prompts for different violation types and languages.
    """

    SYSTEM_PROMPT = (
        "You are an expert software engineer specializing in green software development "
        "and performance optimization. Your goal is to provide optimized code snippets "
        "that fix specific violations while maintaining correctness and readability.\n"
        "Always return ONLY the corrected code snippet in a markdown code block (```language ... ```)."
    )

    # Templates for specific violation types
    # Keys can be (language, violation_keyword) or just violation_keyword

    _TEMPLATES = {
        # Python
        ("python", "loop"): (
            "Optimize the following Python loop for performance and energy efficiency.\n"
            "Consider using vectorization (numpy), list comprehensions, or built-in functions (map, filter) where appropriate.\n"
            "Avoid unnecessary computations inside the loop.\n\n"
            "Violation: {violation}\n"
            "Code:\n```python\n{code}\n```"
        ),
        ("python", "io"): (
            "Optimize the following Python I/O operation for performance and energy efficiency.\n"
            "Consider using buffered I/O, asynchronous I/O (asyncio), or batch processing.\n"
            "Ensure resources are properly managed (context managers).\n\n"
            "Violation: {violation}\n"
            "Code:\n```python\n{code}\n```"
        ),
        ("python", "logic"): (
            "Optimize the following Python logic for computational efficiency.\n"
            "Reduce complexity, remove redundant checks, and use efficient data structures.\n\n"
            "Violation: {violation}\n"
            "Code:\n```python\n{code}\n```"
        ),

        # JavaScript / TypeScript
        ("javascript", "loop"): (
            "Optimize the following JavaScript loop for performance.\n"
            "Consider using `for...of`, `map`, `reduce`, or avoiding layout thrashing if DOM is involved.\n\n"
            "Violation: {violation}\n"
            "Code:\n```javascript\n{code}\n```"
        ),
        ("typescript", "loop"): (
            "Optimize the following TypeScript loop for performance.\n"
            "Consider using `for...of`, `map`, `reduce`, or avoiding layout thrashing if DOM is involved.\n\n"
            "Violation: {violation}\n"
            "Code:\n```typescript\n{code}\n```"
        ),
        ("javascript", "dom"): (
            "Optimize the following JavaScript DOM manipulation.\n"
            "Batch DOM updates, use `documentFragment`, or `requestAnimationFrame` to avoid reflows and repaints.\n\n"
            "Violation: {violation}\n"
            "Code:\n```javascript\n{code}\n```"
        ),
        ("typescript", "dom"): (
            "Optimize the following TypeScript DOM manipulation.\n"
            "Batch DOM updates, use `documentFragment`, or `requestAnimationFrame` to avoid reflows and repaints.\n\n"
            "Violation: {violation}\n"
            "Code:\n```typescript\n{code}\n```"
        ),

        # Generic fallback
        "generic": (
            "Fix the following green software violation.\n"
            "Focus on energy efficiency and performance.\n\n"
            "Violation: {violation}\n"
            "Code:\n```{language}\n{code}\n```"
        )
    }

    @classmethod
    def get_system_prompt(cls) -> str:
        return cls.SYSTEM_PROMPT

    @classmethod
    def get_fix_prompt(cls, language: str, violation_description: str, code_snippet: str) -> str:
        """
        Generate a prompt for fixing a specific violation.
        """
        key = cls._determine_key(language, violation_description)
        template = cls._TEMPLATES.get(key, cls._TEMPLATES["generic"])

        return template.format(
            language=language,
            violation=violation_description,
            code=code_snippet
        )

    @classmethod
    def _determine_key(cls, language: str, violation_description: str):
        """
        Determine the template key based on language and violation description.
        """
        desc_lower = violation_description.lower()
        lang_lower = language.lower()

        # Check for specific keywords in the description
        if "loop" in desc_lower:
            return (lang_lower, "loop")
        if "io" in desc_lower or "file" in desc_lower or "network" in desc_lower:
             return (lang_lower, "io")
        if "dom" in desc_lower or "html" in desc_lower:
             return (lang_lower, "dom")
        if "logic" in desc_lower or "complexity" in desc_lower:
             return (lang_lower, "logic")

        return "generic"
