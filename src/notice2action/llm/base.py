"""
Base Interface and Exceptions for Multi-Provider LLM Integration.
Provides a unified contract for Ollama, OpenRouter, Google Gemini, and Hugging Face.
"""

from __future__ import annotations

import abc
import json
import re
from typing import Dict, Any, Optional, List


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LLMClientError(Exception):
    """Base exception for all LLM client failures."""
    pass


class LLMConfigError(LLMClientError):
    """Raised when provider configuration or credentials are missing/invalid."""
    pass


class LLMAuthError(LLMClientError):
    """Raised when authentication fails (HTTP 401/403)."""
    pass


class LLMConnectionError(LLMClientError):
    """Raised when the provider endpoint or local daemon cannot be reached."""
    pass


class LLMTimeoutError(LLMClientError):
    """Raised when the LLM inference request times out."""
    pass


class LLMRateLimitError(LLMClientError):
    """Raised when the provider rate limits requests (HTTP 429)."""
    pass


class LLMModelError(LLMClientError):
    """Raised when the requested model is missing or unsupported by the provider."""
    pass


# Backward-compatibility aliases for existing Ollama exceptions
OllamaClientError = LLMClientError
OllamaConnectionError = LLMConnectionError
OllamaModelError = LLMModelError
OllamaTimeoutError = LLMTimeoutError


# ---------------------------------------------------------------------------
# JSON Sanitization Helper
# ---------------------------------------------------------------------------

def clean_llm_json_response(raw_text: str) -> str:
    """
    Cleans raw model output:
    1. Removes <thinking>...</thinking> blocks produced by reasoning models.
    2. Strips markdown fences (```json ... ```).
    3. Trims whitespace.
    4. Extracts outermost JSON object.
    5. Cleans trailing commas before closing braces/brackets.
    """
    if not raw_text:
        return ""

    # Remove thinking tags and enclosed thoughts
    cleaned = re.sub(r"<thinking>[\s\S]*?</thinking>", "", raw_text, flags=re.IGNORECASE).strip()

    # Match JSON block inside markdown code fences
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    # Find first { and last } if extra commentary is around it
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace : last_brace + 1]

    # Clean trailing commas before closing braces or brackets (common LLM JSON error)
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

    return cleaned


# ---------------------------------------------------------------------------
# Base LLM Client Interface
# ---------------------------------------------------------------------------

class BaseLLMClient(abc.ABC):
    """Abstract base class defining the unified contract for LLM providers."""

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'ollama', 'openrouter', 'gemini', 'huggingface')."""
        pass

    @property
    @abc.abstractmethod
    def model(self) -> str:
        """Configured model identifier."""
        pass

    @abc.abstractmethod
    def check_health(self) -> Dict[str, Any]:
        """
        Validates connectivity, configuration, and model availability.
        Returns a dictionary with status, model, and diagnostic details.
        """
        pass

    @abc.abstractmethod
    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> str:
        """
        Sends chat completion messages to the provider.
        Returns raw text response.
        """
        pass

    def generate_structured_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Dict[str, Any]:
        """
        Requests structured JSON from the model and parses it into a Python dictionary.
        Applies cleaning, thinking-token stripping, and error diagnostics.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        raw_output = self.generate_chat(messages, json_mode=True, temperature=0.0)
        clean_json_str = clean_llm_json_response(raw_output)

        try:
            return json.loads(clean_json_str)
        except json.JSONDecodeError as e:
            raise LLMClientError(
                f"Failed to parse JSON response from provider '{self.provider_name}' "
                f"(model: {self.model}): {e}. Raw content snippet: {raw_output[:300]}"
            ) from e
