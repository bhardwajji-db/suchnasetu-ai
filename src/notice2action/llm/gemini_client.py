"""
Google Gemini Cloud LLM Adapter for SuchnaSetu AI.
Provides direct integration with Google Generative AI REST API (Gemini 1.5/2.0).
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

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiClient(BaseLLMClient):
    """Adapter for interacting with Google Gemini API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: int = 60,
    ):
        self._api_key = api_key or config.gemini_api_key or config.llm_api_key
        self._model = model or config.gemini_model
        self.timeout = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model

    def check_health(self) -> Dict[str, Any]:
        """Validates configuration and API key status."""
        if not self._api_key or not self._api_key.strip():
            return {
                "provider": "gemini",
                "connected": False,
                "configured": False,
                "target_model": self.model,
                "error": "Missing GEMINI_API_KEY in environment variables.",
            }

        try:
            # Check model metadata
            url = f"{GEMINI_BASE_URL}/{self.model}?key={self._api_key.strip()}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return {
                    "provider": "gemini",
                    "connected": True,
                    "configured": True,
                    "target_model": self.model,
                }
            elif resp.status_code in (401, 403):
                return {
                    "provider": "gemini",
                    "connected": False,
                    "configured": True,
                    "target_model": self.model,
                    "error": "Invalid Gemini API Key (HTTP 401/403).",
                }
            else:
                return {
                    "provider": "gemini",
                    "connected": True,
                    "configured": True,
                    "target_model": self.model,
                    "warning": f"Metadata check returned HTTP {resp.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {
                "provider": "gemini",
                "connected": False,
                "configured": True,
                "target_model": self.model,
                "error": f"Failed to connect to Google Gemini endpoint: {e}",
            }

    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> str:
        """Sends chat generation request to Google Gemini API."""
        if not self._api_key or not self._api_key.strip():
            raise LLMConfigError(
                "Google Gemini API key is not configured. Set GEMINI_API_KEY in your .env file."
            )

        url = f"{GEMINI_BASE_URL}/{self.model}:generateContent?key={self._api_key.strip()}"

        # Separate system instruction from conversational contents
        system_instruction: Optional[str] = None
        contents: List[Dict[str, Any]] = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = content
            else:
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": content}],
                })

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )

            if resp.status_code in (401, 403):
                raise LLMAuthError(
                    f"Gemini authentication failed (HTTP {resp.status_code}): {resp.text}"
                )
            if resp.status_code == 429:
                raise LLMRateLimitError(
                    f"Gemini rate limit exceeded (HTTP 429): {resp.text}"
                )
            if resp.status_code == 404:
                raise LLMModelError(
                    f"Gemini model '{self.model}' not found (HTTP 404): {resp.text}"
                )
            if resp.status_code != 200:
                raise LLMClientError(
                    f"Gemini API error (HTTP {resp.status_code}): {resp.text}"
                )

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise LLMClientError(f"Gemini returned no candidates: {data}")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise LLMClientError("Gemini candidate content has no parts.")

            return parts[0].get("text", "")

        except requests.exceptions.Timeout as e:
            raise LLMTimeoutError(f"Google Gemini inference timed out after {self.timeout}s.") from e
        except requests.exceptions.ConnectionError as e:
            raise LLMConnectionError(f"Failed to connect to Google Gemini endpoint: {e}") from e
        except requests.exceptions.RequestException as e:
            raise LLMClientError(f"Google Gemini request failure: {e}") from e
