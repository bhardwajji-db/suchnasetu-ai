"""
OpenRouter Cloud LLM Adapter for SuchnaSetu AI.
Provides unified access to open and proprietary models via OpenRouter's OpenAI-compatible API.
"""

from __future__ import annotations

import os
import logging
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

logger = logging.getLogger("notice2action.llm.openrouter")

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_AUTH_URL = "https://openrouter.ai/api/v1/auth/key"
DEFAULT_OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"


class OpenRouterClient(BaseLLMClient):
    """Adapter for interacting with OpenRouter cloud inference."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ):
        self._api_key = (
            api_key
            or os.getenv("OPENROUTER_API_KEY")
            or config.openrouter_api_key
            or config.llm_api_key
        )
        self._model = (
            model
            or os.getenv("OPENROUTER_MODEL")
            or config.openrouter_model
            or DEFAULT_OPENROUTER_MODEL
        )
        raw_timeout = timeout_seconds or os.getenv("OPENROUTER_TIMEOUT_SECONDS") or 60
        self.timeout = int(raw_timeout)
        self.max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "4096"))

    @property
    def provider_name(self) -> str:
        return "openrouter"

    @property
    def model(self) -> str:
        return self._model

    def check_health(self) -> Dict[str, Any]:
        """Validates configuration and API key status without leaking credentials."""
        if not self._api_key or not self._api_key.strip():
            return {
                "provider": "openrouter",
                "connected": False,
                "configured": False,
                "target_model": self.model,
                "error": "Missing OPENROUTER_API_KEY in environment variables.",
            }

        try:
            # Lightweight auth check to models/key endpoint
            resp = requests.get(
                OPENROUTER_AUTH_URL,
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
        """Sends chat completion request to OpenRouter API with safe error handling."""
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
            "max_tokens": self.max_tokens,
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

            # Some OpenRouter backends don't accept response_format={"type": "json_object"}
            if resp.status_code == 400 and json_mode and "response_format" in resp.text.lower():
                logger.info(
                    "OpenRouter backend rejected response_format; retrying without JSON mode payload parameter."
                )
                payload.pop("response_format", None)
                resp = requests.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )

            if resp.status_code in (401, 403):
                raise LLMAuthError(
                    f"OpenRouter authentication failed (HTTP {resp.status_code}): Invalid or missing API key."
                )
            if resp.status_code == 402:
                raise LLMAuthError(
                    "OpenRouter account balance is insufficient for the requested model."
                )
            if resp.status_code == 429:
                raise LLMRateLimitError(
                    "OpenRouter rate limit reached (HTTP 429). Please wait before retrying."
                )
            if resp.status_code == 404:
                raise LLMModelError(
                    f"Model '{self.model}' was not found on OpenRouter (HTTP 404)."
                )
            if 500 <= resp.status_code < 600:
                raise LLMConnectionError(
                    f"OpenRouter upstream service error (HTTP {resp.status_code})."
                )
            if resp.status_code != 200:
                raise LLMClientError(
                    f"OpenRouter returned error HTTP {resp.status_code}."
                )

            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise LLMClientError("OpenRouter returned empty choices array.")

            content = choices[0].get("message", {}).get("content", "")
            if not content:
                raise LLMClientError("OpenRouter returned empty message content.")
            return content

        except requests.exceptions.Timeout as e:
            raise LLMTimeoutError(
                f"OpenRouter inference timed out after {self.timeout}s."
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise LLMConnectionError(
                f"Failed to connect to OpenRouter endpoint: {e}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise LLMClientError(f"OpenRouter request failure: {e}") from e
