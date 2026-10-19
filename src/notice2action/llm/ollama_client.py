"""
Local Model Adapter for Gemma 4 via Ollama.
Handles request lifecycle, timeouts, JSON parsing, thinking-token stripping, and error paths.
"""

from __future__ import annotations

import json
import re
from typing import Dict, Any, Optional, List
import requests

from notice2action.config import config


class OllamaClientError(Exception):
    """Base exception for Ollama client failures."""
    pass


class OllamaConnectionError(OllamaClientError):
    """Raised when the Ollama daemon cannot be reached."""
    pass


class OllamaModelError(OllamaClientError):
    """Raised when the requested model is missing or fails on Ollama."""
    pass


class OllamaTimeoutError(OllamaClientError):
    """Raised when local inference times out."""
    pass


def clean_llm_json_response(raw_text: str) -> str:
    """
    Cleans raw model output:
    1. Removes <thinking>...</thinking> blocks produced by reasoning models.
    2. Strips markdown fences (```json ... ```).
    3. Trims whitespace.
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

    return cleaned


class OllamaClient:
    """Adapter for interacting with locally hosted Gemma 4 through Ollama."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ):
        self.base_url = (base_url or config.ollama_base_url).rstrip("/")
        self.model = model or config.ollama_model
        self.timeout = timeout_seconds or config.ollama_timeout_seconds

    def check_health(self) -> Dict[str, Any]:
        """Checks if Ollama is responsive and if the model is loaded."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code != 200:
                raise OllamaConnectionError(
                    f"Ollama server returned HTTP {resp.status_code} at {self.base_url}"
                )
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            has_model = any(
                self.model == m or self.model == m.split(":")[0] or m.startswith(self.model)
                for m in models
            )
            return {
                "connected": True,
                "models": models,
                "has_target_model": has_model,
                "target_model": self.model,
            }
        except requests.exceptions.Timeout as e:
            raise OllamaTimeoutError(
                f"Connection to Ollama at {self.base_url} timed out."
            ) from e
        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. Ensure 'ollama serve' is running ({e})."
            ) from e

    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> str:
        """
        Sends a chat completion request to Gemma 4.
        Returns the raw cleaned assistant text content.
        """
        endpoint = f"{self.base_url}/api/chat"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        if json_mode:
            payload["format"] = "json"

        try:
            resp = requests.post(endpoint, json=payload, timeout=self.timeout)
            if resp.status_code == 404:
                raise OllamaModelError(
                    f"Model '{self.model}' not found in Ollama. Pull it with: 'ollama run {self.model}'"
                )
            if resp.status_code != 200:
                raise OllamaClientError(
                    f"Ollama inference error (HTTP {resp.status_code}): {resp.text}"
                )

            data = resp.json()
            message = data.get("message", {})
            content = message.get("content", "")
            return content

        except requests.exceptions.ConnectionError as e:
            raise OllamaConnectionError(
                f"Failed to connect to Ollama server at {self.base_url}. Is Ollama running?"
            ) from e
        except requests.exceptions.Timeout as e:
            raise OllamaTimeoutError(
                f"Gemma 4 inference timed out after {self.timeout} seconds."
            ) from e
        except requests.exceptions.RequestException as e:
            raise OllamaClientError(f"Ollama request error: {e}") from e

    def generate_structured_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Dict[str, Any]:
        """
        Requests structured JSON from Gemma 4 and parses it into a Python dict.
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
            raise OllamaClientError(
                f"Failed to parse JSON response from Gemma 4: {e}. Raw content: {raw_output[:300]}"
            ) from e
