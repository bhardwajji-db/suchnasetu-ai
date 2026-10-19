"""
Configuration and Preflight Diagnostics for Notice2Action AI.
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


@dataclass
class AppConfig:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma4:latest")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
    tesseract_cmd: Optional[str] = _find_tesseract_cmd()
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    max_image_dimension: int = int(os.getenv("MAX_IMAGE_DIMENSION", "4096"))
    allowed_extensions: List[str] = field(
        default_factory=lambda: os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,webp,txt").split(",")
    )
    synthetic_fixtures_dir: Path = PROJECT_ROOT / "tests" / "fixtures"


config = AppConfig()


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
    - Ollama server connectivity
    - Gemma 4 model availability
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

    # 2. Tesseract OCR Check
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

    # 3. Ollama Server Connectivity
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

    # 4. Target Model (Gemma 4) Availability
    if ollama_ok:
        target_model = cfg.ollama_model
        # Check exact or prefix match (e.g. gemma4:latest or gemma4)
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

    # Calculate overall status
    if any(i.status == "error" for i in report.items):
        report.overall_status = "error"
    elif any(i.status == "warning" for i in report.items):
        report.overall_status = "warning"
    else:
        report.overall_status = "ok"

    return report
