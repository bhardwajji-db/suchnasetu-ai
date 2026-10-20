"""
Hugging Face Inference API Cloud Adapter for Notice2Action AI.
Provides access to hosted open models via Hugging Face Inference Serverless router.
"""

from __future__ import annotations

import os
import time
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

HF_ROUTER_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"


class HuggingFaceClient(BaseLLMClient):
    """Adapter for interacting with Hugging Face hosted inference models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: int = 90,
    ):
        self._api_key = api_key or config.huggingface_api_key or config.llm_api_key
        self._model = model or config.huggingface_model
        self.timeout = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "huggingface"

    @property
    def model(self) -> str:
        return self._model

    def check_health(self) -> Dict[str, Any]:
        """Validates configuration and API token status."""
        if not self._api_key or not self._api_key.strip():
            return {
                "provider": "huggingface",
                "connected": False,
                "configured": False,
                "target_model": self.model,
                "error": "Missing HUGGINGFACE_API_KEY in environment variables.",
            }

        try:
            # Query whoami / status check
            resp = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers={"Authorization": f"Bearer {self._api_key.strip()}"},
                timeout=5,
            )
            if resp.status_code == 200:
                user_info = resp.json()
                return {
                    "provider": "huggingface",
                    "connected": True,
                    "configured": True,
                    "target_model": self.model,
                    "user": user_info.get("name"),
                }
            elif resp.status_code in (401, 403):
                return {
                    "provider": "huggingface",
                    "connected": False,
                    "configured": True,
                    "target_model": self.model,
                    "error": "Invalid Hugging Face API Token (HTTP 401/403).",
                }
            else:
                return {
                    "provider": "huggingface",
                    "connected": True,
                    "configured": True,
                    "target_model": self.model,
                    "warning": f"Status check returned HTTP {resp.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {
                "provider": "huggingface",
                "connected": False,
                "configured": True,
                "target_model": self.model,
                "error": f"Failed to connect to Hugging Face endpoint: {e}",
            }

    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> str:
        """Sends chat completion request to Hugging Face serverless router."""
        if not self._api_key or not self._api_key.strip():
            raise LLMConfigError(
                "Hugging Face API key is not configured. Set HUGGINGFACE_API_KEY in your .env file."
            )

        headers = {
            "Authorization": f"Bearer {self._api_key.strip()}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4096,
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = requests.post(
                HF_ROUTER_URL,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )

            # If model is currently loading (503), check for estimated time
            if resp.status_code == 503:
                data = resp.json() if resp.content else {}
                estimated_time = data.get("estimated_time", 20.0)
                raise LLMClientError(
                    f"Hugging Face model '{self.model}' is currently loading (estimated wait: {estimated_time}s). "
                    "Please retry in a moment."
                )

            if resp.status_code in (401, 403):
                raise LLMAuthError(
                    f"Hugging Face authentication failed (HTTP {resp.status_code}): {resp.text}"
                )
            if resp.status_code == 429:
                raise LLMRateLimitError(
                    f"Hugging Face rate limit reached (HTTP 429): {resp.text}"
                )
            if resp.status_code == 404:
                raise LLMModelError(
                    f"Model '{self.model}' not found on Hugging Face (HTTP 404): {resp.text}"
                )
            if resp.status_code != 200:
                raise LLMClientError(
                    f"Hugging Face error (HTTP {resp.status_code}): {resp.text}"
                )

            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise LLMClientError("Hugging Face returned empty choices array.")

            content = choices[0].get("message", {}).get("content", "")
            return content

        except requests.exceptions.Timeout as e:
            raise LLMTimeoutError(f"Hugging Face inference timed out after {self.timeout}s.") from e
        except requests.exceptions.ConnectionError as e:
            raise LLMConnectionError(f"Failed to connect to Hugging Face endpoint: {e}") from e
        except requests.exceptions.RequestException as e:
            raise LLMClientError(f"Hugging Face request failure: {e}") from e
