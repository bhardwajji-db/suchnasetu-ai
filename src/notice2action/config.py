"""
Configuration and Preflight Diagnostics for SuchnaSetu AI.
"""

from __future__ import annotations

import os
import shutil
import sys
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
import requests

# Load .env if present
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _find_tesseract_cmd() -> Optional[str]:
    """Auto-detect Tesseract binary on Windows and standard paths."""
    env_cmd = os.getenv("TESSERACT_CMD")
    if env_cmd and Path(env_cmd).is_file():
        return env_cmd

    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        str(Path.home() / r"AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    for c in candidates:
        if Path(c).is_file():
            return c

    system_which = shutil.which("tesseract")
    if system_which:
        return system_which
    return None


def _find_tessdata_dir() -> Optional[str]:
    """Auto-detects project or system tessdata directory with Hindi/English language packs."""
    env_dir = os.getenv("TESSDATA_PREFIX")
    if env_dir and Path(env_dir).is_dir():
        return env_dir

    candidates = [
        PROJECT_ROOT / "assets" / "tessdata",
        Path(r"C:\Program Files\Tesseract-OCR\tessdata"),
        Path(r"C:\Program Files (x86)\Tesseract-OCR\tessdata"),
    ]
    for c in candidates:
        if (c / "hin.traineddata").is_file() or (c / "eng.traineddata").is_file():
            return str(c)
    return None


@dataclass
class AppConfig:
    # LLM Provider selection: "ollama", "openrouter", "gemini", "huggingface"
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama").lower()
    llm_api_key: Optional[str] = os.getenv("LLM_API_KEY")

    # Local Ollama
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma4:latest")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

    # Cloud Provider 1: OpenRouter
    openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free")

    # Cloud Provider 2: Google Gemini
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Cloud Provider 3: Hugging Face
    huggingface_api_key: Optional[str] = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
    huggingface_model: str = os.getenv("HUGGINGFACE_MODEL", "google/gemma-2-9b-it")

    # OCR Engine
    ocr_engine: str = os.getenv("OCR_ENGINE", "tesseract").lower()
    tesseract_cmd: Optional[str] = _find_tesseract_cmd()
    tessdata_dir: Optional[str] = _find_tessdata_dir()

    # Session Storage
    session_storage_dir: Path = PROJECT_ROOT / os.getenv("SESSION_STORAGE_DIR", ".sessions")
    session_ttl_hours: int = int(os.getenv("SESSION_TTL_HOURS", "24"))

    # Ingestion & Limits
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    max_image_dimension: int = int(os.getenv("MAX_IMAGE_DIMENSION", "4096"))
    max_pdf_pages: int = int(os.getenv("MAX_PDF_PAGES", "30"))
    allowed_extensions: List[str] = field(
        default_factory=lambda: [e.strip().lower() for e in os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,webp,txt,pdf").split(",") if e.strip()]
    )
    synthetic_fixtures_dir: Path = PROJECT_ROOT / "tests" / "fixtures"


config = AppConfig()

# Configure environment for Tesseract if local tessdata directory detected
if config.tessdata_dir and "TESSDATA_PREFIX" not in os.environ:
    os.environ["TESSDATA_PREFIX"] = config.tessdata_dir


@dataclass
class DiagnosticItem:
    name: str
    status: str  # "ok", "warning", "error"
    details: str
    remedy: Optional[str] = None


@dataclass
class PreflightReport:
    items: List[DiagnosticItem] = field(default_factory=list)
    overall_status: str = "ok"

    def is_ready_for_inference(self) -> bool:
        return all(i.status != "error" for i in self.items)


def run_preflight_diagnostics(cfg: Optional[AppConfig] = None) -> PreflightReport:
    """
    Runs comprehensive diagnostic checks on:
    - Python environment
    - Tesseract OCR engine and language support
    - Configured LLM provider (Ollama, OpenRouter, Gemini, or Hugging Face)
    - Session storage directory
    """
    if cfg is None:
        cfg = config

    report = PreflightReport()

    # 1. Python Check
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 11):
        report.items.append(
            DiagnosticItem("Python Runtime", "ok", f"Python {py_ver} ({sys.executable})")
        )
    else:
        report.items.append(
            DiagnosticItem(
                "Python Runtime",
                "warning",
                f"Python {py_ver} detected. Recommended >= 3.11",
                "Install Python 3.11 or higher.",
            )
        )

    # 2. OCR Engine Check
    if cfg.ocr_engine == "rapidocr":
        try:
            import rapidocr_onnxruntime  # type: ignore # noqa: F401
            report.items.append(
                DiagnosticItem("RapidOCR Engine", "ok", "RapidOCR with ONNX Runtime is installed.")
            )
        except ImportError:
            report.items.append(
                DiagnosticItem(
                    "RapidOCR Engine",
                    "warning",
                    "RapidOCR requested but rapidocr_onnxruntime is not installed. Falling back to Tesseract.",
                    "Install with: pip install rapidocr-onnxruntime",
                )
            )

    if cfg.tesseract_cmd and Path(cfg.tesseract_cmd).is_file():
        try:
            ver_res = subprocess.run(
                [cfg.tesseract_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            first_line = ver_res.stdout.splitlines()[0] if ver_res.stdout else "Installed"

            # Check installed languages
            langs_res = subprocess.run(
                [cfg.tesseract_cmd, "--list-langs"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            langs = [line.strip() for line in langs_res.stdout.splitlines()[1:] if line.strip()]
            report.items.append(
                DiagnosticItem(
                    "Tesseract OCR",
                    "ok",
                    f"{first_line} at {cfg.tesseract_cmd}. Languages: {', '.join(langs)}",
                )
            )
        except Exception as e:
            report.items.append(
                DiagnosticItem(
                    "Tesseract OCR",
                    "warning",
                    f"Binary found at {cfg.tesseract_cmd} but check failed: {e}",
                    "Verify Tesseract permissions.",
                )
            )
    else:
        report.items.append(
            DiagnosticItem(
                "Tesseract OCR",
                "warning",
                "Tesseract binary not found in standard paths.",
                "Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki or specify TESSERACT_CMD in .env.",
            )
        )

    # 3. Document Processing (PDF Support)
    try:
        import pypdf
        report.items.append(
            DiagnosticItem(
                "PDF Engine (pypdf)",
                "ok",
                f"Digital & scanned PDF extraction active (pypdf v{pypdf.__version__}).",
            )
        )
    except Exception as e:
        report.items.append(
            DiagnosticItem(
                "PDF Engine (pypdf)",
                "warning",
                f"pypdf library not available: {e}",
                "Run pip install pypdf",
            )
        )

    # 4. LLM Provider Diagnostics
    provider = cfg.llm_provider
    report.items.append(
        DiagnosticItem("Configured LLM Provider", "ok", f"Active provider: '{provider}'")
    )

    if provider == "ollama":
        # Ollama Server Connectivity
        ollama_ok = False
        models_found: List[str] = []
        try:
            resp = requests.get(f"{cfg.ollama_base_url}/api/tags", timeout=4)
            if resp.status_code == 200:
                ollama_ok = True
                data = resp.json()
                models_found = [m.get("name", "") for m in data.get("models", [])]
                report.items.append(
                    DiagnosticItem(
                        "Ollama Server",
                        "ok",
                        f"Connected to {cfg.ollama_base_url}. Found {len(models_found)} model(s).",
                    )
                )
            else:
                report.items.append(
                    DiagnosticItem(
                        "Ollama Server",
                        "error",
                        f"Server responded with HTTP {resp.status_code}",
                        "Check Ollama server logs.",
                    )
                )
        except Exception as e:
            report.items.append(
                DiagnosticItem(
                    "Ollama Server",
                    "error",
                    f"Cannot connect to {cfg.ollama_base_url} ({e})",
                    "Start Ollama with 'ollama serve' in PowerShell.",
                )
            )

        # Target Model (Gemma 4) Check
        if ollama_ok:
            target_model = cfg.ollama_model
            model_present = any(
                target_model == m or target_model == m.split(":")[0] or m.startswith(target_model)
                for m in models_found
            )
            if model_present:
                report.items.append(
                    DiagnosticItem(
                        f"LLM Model ({target_model})",
                        "ok",
                        f"Model '{target_model}' is downloaded and ready in Ollama.",
                    )
                )
            else:
                report.items.append(
                    DiagnosticItem(
                        f"LLM Model ({target_model})",
                        "error",
                        f"Model '{target_model}' was not found in Ollama tags: {models_found}",
                        f"Run 'ollama run {target_model}' or configure OLLAMA_MODEL in .env.",
                    )
                )
        else:
            report.items.append(
                DiagnosticItem(
                    f"LLM Model ({cfg.ollama_model})",
                    "warning",
                    "Skipped model check because Ollama server is unreachable.",
                    "Ensure Ollama server is running first.",
                )
            )

    elif provider == "openrouter":
        api_key = cfg.openrouter_api_key or cfg.llm_api_key
        if api_key and api_key.strip():
            report.items.append(
                DiagnosticItem(
                    "OpenRouter API Key",
                    "ok",
                    f"Configured (model: {cfg.openrouter_model})",
                )
            )
        else:
            report.items.append(
                DiagnosticItem(
                    "OpenRouter API Key",
                    "warning",
                    "Missing OPENROUTER_API_KEY in .env.",
                    "Add OPENROUTER_API_KEY=<your_key> to .env to enable cloud inference via OpenRouter.",
                )
            )

    elif provider == "gemini":
        api_key = cfg.gemini_api_key or cfg.llm_api_key
        if api_key and api_key.strip():
            report.items.append(
                DiagnosticItem(
                    "Google Gemini API Key",
                    "ok",
                    f"Configured (model: {cfg.gemini_model})",
                )
            )
        else:
            report.items.append(
                DiagnosticItem(
                    "Google Gemini API Key",
                    "warning",
                    "Missing GEMINI_API_KEY in .env.",
                    "Add GEMINI_API_KEY=<your_key> to .env to enable Google Gemini inference.",
                )
            )

    elif provider == "huggingface":
        api_key = cfg.huggingface_api_key or cfg.llm_api_key
        if api_key and api_key.strip():
            report.items.append(
                DiagnosticItem(
                    "Hugging Face API Key",
                    "ok",
                    f"Configured (model: {cfg.huggingface_model})",
                )
            )
        else:
            report.items.append(
                DiagnosticItem(
                    "Hugging Face API Key",
                    "warning",
                    "Missing HUGGINGFACE_API_KEY in .env.",
                    "Add HUGGINGFACE_API_KEY=<your_key> to .env to enable Hugging Face inference.",
                )
            )

    # Calculate overall status
    if any(i.status == "error" for i in report.items):
        report.overall_status = "error"
    elif any(i.status == "warning" for i in report.items):
        report.overall_status = "warning"
    else:
        report.overall_status = "ok"

    return report
