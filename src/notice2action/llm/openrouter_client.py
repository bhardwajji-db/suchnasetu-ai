"""
OpenRouter Cloud LLM Adapter for SuchnaSetu AI.
Provides unified access to open and proprietary models via OpenRouter's OpenAI-compatible API.
"""

from __future__ import annotations

import os
from typing import Dict, Any, Optional, List
import requests

from notice2action.config import config
from notice2action.llm.base import (
    BaseLLMClient,
    LLMClientError,
    LLMConfigError,
    LLMAuthError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMModelError,
)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterClient(BaseLLMClient):
    """Adapter for interacting with OpenRouter cloud inference."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: int = 60,
    ):
        self._api_key = api_key or config.openrouter_api_key or config.llm_api_key
        self._model = model or config.openrouter_model
        self.timeout = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "openrouter"

    @property
    def model(self) -> str:
        return self._model

    def check_health(self) -> Dict[str, Any]:
        """Validates configuration and API key status."""
        if not self._api_key or not self._api_key.strip():
            return {
                "provider": "openrouter",
                "connected": False,
                "configured": False,
                "target_model": self.model,
                "error": "Missing OPENROUTER_API_KEY in environment variables.",
            }

        try:
            # Lightweight auth check to models endpoint
            resp = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {self._api_key.strip()}"},
                timeout=5,
            )
            if resp.status_code == 200:
                return {
                    "provider": "openrouter",
                    "connected": True,
                    "configured": True,
                    "target_model": self.model,
                }
            elif resp.status_code in (401, 403):
                return {
                    "provider": "openrouter",
                    "connected": False,
                    "configured": True,
                    "target_model": self.model,
                    "error": "Invalid OpenRouter API Key (HTTP 401/403).",
                }
            else:
                return {
                    "provider": "openrouter",
                    "connected": True,
                    "configured": True,
                    "target_model": self.model,
                    "warning": f"Auth check returned HTTP {resp.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {
                "provider": "openrouter",
                "connected": False,
                "configured": True,
                "target_model": self.model,
                "error": f"Failed to connect to OpenRouter: {e}",
            }

    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> str:
        """Sends chat completion request to OpenRouter API."""
        if not self._api_key or not self._api_key.strip():
            raise LLMConfigError(
                "OpenRouter API key is not configured. Set OPENROUTER_API_KEY in your .env file."
            )

        headers = {
            "Authorization": f"Bearer {self._api_key.strip()}",
            "HTTP-Referer": "https://github.com/bhardwajji-db/suchnasetu-ai",
            "X-Title": "SuchnaSetu AI",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )

            if resp.status_code in (401, 403):
                raise LLMAuthError(
                    f"OpenRouter authentication failed (HTTP {resp.status_code}): {resp.text}"
                )
            if resp.status_code == 429:
                raise LLMRateLimitError(
                    f"OpenRouter rate limit reached (HTTP 429): {resp.text}"
                )
            if resp.status_code == 404:
                raise LLMModelError(
                    f"Model '{self.model}' not found on OpenRouter (HTTP 404): {resp.text}"
                )
            if resp.status_code != 200:
                raise LLMClientError(
                    f"OpenRouter error (HTTP {resp.status_code}): {resp.text}"
                )

            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise LLMClientError("OpenRouter returned empty choices array.")

            content = choices[0].get("message", {}).get("content", "")
            return content

        except requests.exceptions.Timeout as e:
            raise LLMTimeoutError(f"OpenRouter inference timed out after {self.timeout}s.") from e
        except requests.exceptions.ConnectionError as e:
            raise LLMConnectionError(f"Failed to connect to OpenRouter endpoint: {e}") from e
        except requests.exceptions.RequestException as e:
            raise LLMClientError(f"OpenRouter request failure: {e}") from e
