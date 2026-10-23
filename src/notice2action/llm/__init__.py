"""
SuchnaSetu AI — Multi-Provider LLM Package
Unified interfaces, local Ollama client, and cloud adapters for OpenRouter, Gemini, and Hugging Face.
"""

from notice2action.llm.base import (
    BaseLLMClient,
    clean_llm_json_response,
    LLMClientError,
    LLMConfigError,
    LLMAuthError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMModelError,
    OllamaClientError,
    OllamaConnectionError,
    OllamaModelError,
    OllamaTimeoutError,
)
from notice2action.llm.ollama_client import OllamaClient
from notice2action.llm.openrouter_client import OpenRouterClient
from notice2action.llm.gemini_client import GeminiClient
from notice2action.llm.huggingface_client import HuggingFaceClient
from notice2action.llm.factory import get_llm_client, get_all_provider_statuses

__all__ = [
    "BaseLLMClient",
    "OllamaClient",
    "OpenRouterClient",
    "GeminiClient",
    "HuggingFaceClient",
    "get_llm_client",
    "get_all_provider_statuses",
    "clean_llm_json_response",
    "LLMClientError",
    "LLMConfigError",
    "LLMAuthError",
    "LLMConnectionError",
    "LLMTimeoutError",
    "LLMRateLimitError",
    "LLMModelError",
    "OllamaClientError",
    "OllamaConnectionError",
    "OllamaModelError",
    "OllamaTimeoutError",
]
