"""
Hugging Face Inference Providers API Cloud Adapter for SuchnaSetu AI.
Provides access to hosted Gemma 4 and open models via Hugging Face Serverless Router (OpenAI-compatible).
"""

from __future__ import annotations

import logging
import os
import re
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

logger = logging.getLogger(__name__)

# Hugging Face Serverless Router (OpenAI-compatible chat completion endpoint)
HF_ROUTER_V1_URL = "https://router.huggingface.co/v1/chat/completions"


def _sanitize_error_text(text: str, token: Optional[str] = None) -> str:
    """Strips secret tokens and authorization credentials from error strings."""
    if not text:
        return ""
    sanitized = text
    if token and len(token) > 5:
        sanitized = sanitized.replace(token, "[REDACTED_HF_TOKEN]")
    # Strip any Bearer headers or hf_ token patterns
    sanitized = re.sub(r"Bearer\s+hf_[A-Za-z0-9_]+", "Bearer [REDACTED_TOKEN]", sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r"hf_[A-Za-z0-9_]{15,}", "[REDACTED_HF_TOKEN]", sanitized)
    return sanitized


class HuggingFaceClient(BaseLLMClient):
    """
    Adapter for interacting with Hugging Face hosted inference models
    via the official Hugging Face Serverless Inference Providers router.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        timeout_seconds: int = 120,
    ):
        raw_token = (
            api_key
            or getattr(config, "hf_token", None)
            or config.huggingface_api_key
            or config.llm_api_key
        )
        self._api_key = raw_token.strip() if raw_token and isinstance(raw_token, str) else None
        self._model = (
            model
            or getattr(config, "huggingface_model", None)
            or "google/gemma-4-26B-A4B"
        ).strip()
        self.provider_routing = (
            provider
            or getattr(config, "hf_provider", "auto")
            or "auto"
        ).strip()
        self.timeout = int(timeout_seconds)

    @property
    def provider_name(self) -> str:
        return "huggingface"

    @property
    def model(self) -> str:
        return self._model

    def check_health(self) -> Dict[str, Any]:
        """
        Validates configuration and API token status against Hugging Face.
        Never reveals secret tokens in output.
        """
        if not self._api_key:
            return {
                "provider": "huggingface",
                "connected": False,
                "configured": False,
                "target_model": self.model,
                "provider_routing": self.provider_routing,
                "error": "Missing HF_TOKEN in environment variables or .env file.",
            }

        try:
            # Query whoami endpoint to verify authentication and account scope
            resp = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=8,
            )
            if resp.status_code == 200:
                user_info = resp.json()
                username = user_info.get("name", "authenticated_user")
                return {
                    "provider": "huggingface",
                    "connected": True,
                    "configured": True,
                    "target_model": self.model,
                    "provider_routing": self.provider_routing,
                    "user": username,
                    "account_type": user_info.get("type", "user"),
                }
            elif resp.status_code in (401, 403):
                return {
                    "provider": "huggingface",
                    "connected": False,
                    "configured": True,
                    "target_model": self.model,
                    "provider_routing": self.provider_routing,
                    "error": "Invalid Hugging Face API Token (HTTP 401/403). Check HF_TOKEN permissions.",
                }
            else:
                return {
                    "provider": "huggingface",
                    "connected": True,
                    "configured": True,
                    "target_model": self.model,
                    "provider_routing": self.provider_routing,
                    "warning": f"Status check returned HTTP {resp.status_code}",
                }
        except requests.exceptions.Timeout:
            return {
                "provider": "huggingface",
                "connected": False,
                "configured": True,
                "target_model": self.model,
                "provider_routing": self.provider_routing,
                "error": "Timeout connecting to Hugging Face auth verification endpoint.",
            }
        except requests.exceptions.RequestException as e:
            sanitized_err = _sanitize_error_text(str(e), self._api_key)
            return {
                "provider": "huggingface",
                "connected": False,
                "configured": True,
                "target_model": self.model,
                "provider_routing": self.provider_routing,
                "error": f"Failed to connect to Hugging Face endpoint: {sanitized_err}",
            }

    def _call_inference_client(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """Sends chat completion request to Hugging Face serverless inference router."""
        headers = {
            "Authorization": f"Bearer {self._api_key.strip()}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = requests.post(
                HF_ROUTER_V1_URL,
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
                    f"Hugging Face authentication failed (HTTP {resp.status_code}): {_sanitize_error_text(resp.text, self._api_key)}"
                )
            if resp.status_code == 429:
                raise LLMRateLimitError(
                    f"Hugging Face rate limit reached (HTTP 429): {_sanitize_error_text(resp.text, self._api_key)}"
                )
            if resp.status_code == 404:
                raise LLMModelError(
                    f"Model '{self.model}' not found on Hugging Face (HTTP 404): {_sanitize_error_text(resp.text, self._api_key)}"
                )
            if resp.status_code != 200:
                # If provider does not support response_format, retry once without it
                if json_mode and resp.status_code == 400 and "response_format" in resp.text.lower():
                    logger.info("Provider does not support response_format; retrying without JSON schema constraint.")
                    payload.pop("response_format", None)
                    retry_resp = requests.post(
                        HF_ROUTER_V1_URL,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout,
                    )
                    if retry_resp.status_code == 200:
                        data = retry_resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0].get("message", {}).get("content", "")
                raise LLMClientError(
                    f"Hugging Face error (HTTP {resp.status_code}): {_sanitize_error_text(resp.text, self._api_key)}"
                )

            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise LLMClientError("Hugging Face returned empty choices array.")

            content = choices[0].get("message", {}).get("content", "")
            return content

        except requests.exceptions.Timeout as e:
            raise LLMTimeoutError(
                f"Hugging Face inference timed out after {self.timeout}s on model '{self.model}'."
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise LLMConnectionError(
                f"Failed to connect to Hugging Face endpoint: {_sanitize_error_text(str(e), self._api_key)}"
            ) from e
        except (LLMAuthError, LLMConfigError, LLMRateLimitError, LLMModelError, LLMClientError, LLMTimeoutError, LLMConnectionError):
            raise
        except Exception as e:
            raise LLMClientError(
                f"Hugging Face request failure: {_sanitize_error_text(str(e), self._api_key)}"
            ) from e

    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> str:
        """
        Sends chat completion messages to Hugging Face hosted inference.
        Includes bounded retries for transient 503 model-loading or network hiccups.
        """
        if not self._api_key or not self._api_key.strip():
            raise LLMConfigError(
                "Hugging Face API token is not configured. Set HF_TOKEN or HUGGINGFACE_API_KEY in your environment or .env file."
            )

        max_retries = 2
        last_exception: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            try:
                return self._call_inference_client(
                    messages=messages,
                    json_mode=json_mode,
                    temperature=temperature,
                    max_tokens=4096,
                )
            except (LLMAuthError, LLMConfigError, LLMModelError):
                # Never retry client config, auth or missing model errors
                raise
            except LLMClientError as e:
                # Retry only if model is loading / 503
                if "currently loading" in str(e).lower() or "overloaded" in str(e).lower():
                    last_exception = e
                    if attempt < max_retries:
                        sleep_time = 2.0 * (attempt + 1)
                        logger.warning(
                            f"Model '{self.model}' loading (attempt {attempt + 1}/{max_retries + 1}). "
                            f"Retrying in {sleep_time}s..."
                        )
                        time.sleep(sleep_time)
                        continue
                raise
            except LLMConnectionError as e:
                last_exception = e
                if attempt < max_retries:
                    sleep_time = 1.5 * (attempt + 1)
                    logger.warning(
                        f"Transient connection failure (attempt {attempt + 1}/{max_retries + 1}). "
                        f"Retrying in {sleep_time}s..."
                    )
                    time.sleep(sleep_time)
                    continue
                raise

        if last_exception:
            raise last_exception
        raise LLMClientError("Inference failed after retry attempts.")
