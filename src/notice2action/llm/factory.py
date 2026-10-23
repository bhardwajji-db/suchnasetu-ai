"""
LLM Provider Factory and Discovery for SuchnaSetu AI.
Instantiates the active client based on configuration, with fallback and status tracking.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List, Type
from notice2action.config import config
from notice2action.llm.base import BaseLLMClient, LLMConfigError
from notice2action.llm.ollama_client import OllamaClient
from notice2action.llm.openrouter_client import OpenRouterClient
from notice2action.llm.gemini_client import GeminiClient
from notice2action.llm.huggingface_client import HuggingFaceClient

PROVIDER_MAP: Dict[str, Type[BaseLLMClient]] = {
    "ollama": OllamaClient,
    "openrouter": OpenRouterClient,
    "gemini": GeminiClient,
    "huggingface": HuggingFaceClient,
}


def get_llm_client(provider_name: Optional[str] = None) -> BaseLLMClient:
    """
    Returns an instantiated BaseLLMClient for the selected or configured provider.
    Defaults to config.llm_provider ('ollama').
    """
    chosen = (provider_name or config.llm_provider or "ollama").lower().strip()
    client_cls = PROVIDER_MAP.get(chosen)

    if not client_cls:
        valid = ", ".join(PROVIDER_MAP.keys())
        raise LLMConfigError(
            f"Unsupported LLM provider '{chosen}'. Supported providers: {valid}"
        )

    return client_cls()


def get_all_provider_statuses() -> List[Dict[str, Any]]:
    """
    Returns the configuration and readiness status of all supported providers.
    Does not crash if credentials are absent.
    """
    statuses = []
    active_provider = config.llm_provider

    # 1. Ollama
    statuses.append({
        "id": "ollama",
        "name": "Ollama (Local / Offline)",
        "is_active": active_provider == "ollama",
        "is_local": True,
        "requires_api_key": False,
        "model": config.ollama_model,
        "endpoint": config.ollama_base_url,
        "key_configured": True,
    })

    # 2. OpenRouter
    openrouter_has_key = bool(config.openrouter_api_key or config.llm_api_key)
    statuses.append({
        "id": "openrouter",
        "name": "OpenRouter (Cloud Router)",
        "is_active": active_provider == "openrouter",
        "is_local": False,
        "requires_api_key": True,
        "model": config.openrouter_model,
        "endpoint": "https://openrouter.ai/api/v1",
        "key_configured": openrouter_has_key,
    })

    # 3. Google Gemini
    gemini_has_key = bool(config.gemini_api_key or config.llm_api_key)
    statuses.append({
        "id": "gemini",
        "name": "Google Gemini (Cloud)",
        "is_active": active_provider == "gemini",
        "is_local": False,
        "requires_api_key": True,
        "model": config.gemini_model,
        "endpoint": "https://generativelanguage.googleapis.com",
        "key_configured": gemini_has_key,
    })

    # 4. Hugging Face
    hf_has_key = bool(config.huggingface_api_key or config.llm_api_key)
    statuses.append({
        "id": "huggingface",
        "name": "Hugging Face Inference (Cloud)",
        "is_active": active_provider == "huggingface",
        "is_local": False,
        "requires_api_key": True,
        "model": config.huggingface_model,
        "endpoint": "https://router.huggingface.co/hf-inference/v1",
        "key_configured": hf_has_key,
    })

    return statuses
