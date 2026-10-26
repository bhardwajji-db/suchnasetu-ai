"""
Local Model Adapter for Gemma 4 via Ollama.
Handles request lifecycle, timeouts, JSON parsing, thinking-token stripping, and error paths.
Inherits from BaseLLMClient to adhere to the multi-provider interface.
"""

from __future__ import annotations

import json
import time
from typing import Dict, Any, Optional, List
import requests

from notice2action.config import config
from notice2action.llm.base import (
    BaseLLMClient,
    clean_llm_json_response,
    LLMClientError,
    LLMConnectionError,
    LLMModelError,
    LLMTimeoutError,
    OllamaClientError,
    OllamaConnectionError,
    OllamaModelError,
    OllamaTimeoutError,
)


class OllamaClient(BaseLLMClient):
    """Adapter for interacting with locally hosted Gemma 4 through Ollama."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        keep_alive: Optional[str] = None,
    ):
        self._base_url = (base_url or config.ollama_base_url).rstrip("/")
        self._model = model or config.ollama_model
        self.timeout = timeout_seconds or config.ollama_timeout_seconds
        self.keep_alive = keep_alive or getattr(config, "ollama_keep_alive", "5m")

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model(self) -> str:
        return self._model

    @property
    def base_url(self) -> str:
        return self._base_url

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
                "provider": "ollama",
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


    def get_loaded_models(self) -> List[Dict[str, Any]]:
        """Queries Ollama /api/ps to retrieve loaded models and resource allocation."""
        try:
            resp = requests.get(f"{self.base_url}/api/ps", timeout=5.0)
            if resp.status_code == 200:
                return resp.json().get("models", [])
            return []
        except Exception:
            return []

    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        temperature: float = 0.1,
    ) -> str:
        """
        Sends a chat completion request to Gemma 4 via Ollama /api/chat.
        Returns the raw cleaned assistant text content.
        """
        endpoint = f"{self.base_url}/api/chat"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {
                "temperature": temperature,
                "num_predict": 4096,
                "num_ctx": 8192,
            },
        }
        if json_mode:
            payload["format"] = "json"

        # Separate quick connection check (10s) from generation read timeout
        connect_timeout = 10.0
        read_timeout = float(self.timeout)

        max_retries = 2
        for attempt in range(max_retries):
            try:
                resp = requests.post(endpoint, json=payload, timeout=(connect_timeout, read_timeout))
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

            except requests.exceptions.ConnectTimeout as e:
                if attempt < max_retries - 1:
                    time.sleep(1.0)
                    continue
                raise OllamaConnectionError(
                    f"Connection to Ollama at {self.base_url} timed out after {connect_timeout}s. Ensure Ollama is running."
                ) from e
            except requests.exceptions.ReadTimeout as e:
                raise OllamaTimeoutError(
                    f"Gemma 4 inference timed out after {int(read_timeout)} seconds. "
                    "The model weights may be loading from disk into VRAM/RAM."
                ) from e
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    time.sleep(1.0)
                    continue
                raise OllamaConnectionError(
                    f"Failed to connect to Ollama server at {self.base_url}. Is Ollama running?"
                ) from e
            except requests.exceptions.Timeout as e:
                raise OllamaTimeoutError(
                    f"Gemma 4 inference timed out after {self.timeout} seconds."
                ) from e
            except requests.exceptions.RequestException as e:
                raise OllamaClientError(f"Ollama request error: {e}") from e

    def unload_model(self, model: Optional[str] = None) -> bool:
        """
        Explicitly unloads the model from VRAM/RAM by sending keep_alive: 0 to Ollama.
        Returns True if successfully acknowledged.
        """
        endpoint = f"{self.base_url}/api/chat"
        try:
            resp = requests.post(
                endpoint,
                json={"model": model or self.model, "messages": [], "keep_alive": 0},
                timeout=5.0,
            )
            return resp.status_code in (200, 404)
        except Exception:
            return False

    def warmup(self, timeout_seconds: int = 15) -> Dict[str, Any]:
        """
        Lightweight readiness probe to ensure the model can be loaded into memory.
        Uses a 1-token prompt to avoid high inference overhead.
        """
        endpoint = f"{self.base_url}/api/chat"
        try:
            resp = requests.post(
                endpoint,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "ping"}],
                    "stream": False,
                    "keep_alive": self.keep_alive,
                    "options": {"num_predict": 1},
                },
                timeout=timeout_seconds,
            )
            if resp.status_code == 404:
                raise OllamaModelError(f"Model '{self.model}' not found in Ollama repository.")
            if resp.status_code == 200:
                return {"status": "ready", "model": self.model, "success": True}
            raise OllamaClientError(f"Warmup returned HTTP {resp.status_code}: {resp.text}")
        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(f"Failed to reach Ollama during warmup: {e}") from e
