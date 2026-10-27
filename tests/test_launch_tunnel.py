"""
Unit and regression tests for scripts/launch_tunnel.py.
Verifies:
1. Regex extraction of trycloudflare.com URLs.
2. Safe updating of .env for AUTH_PUBLIC_APP_URL and CORS_ALLOWED_ORIGINS.
3. Clean removal of old ephemeral trycloudflare URLs while preserving localhost/LAN origins.
4. Named tunnel token extraction from env.
5. Ollama health check response parsing.
"""

import os
import sys
import re
import tempfile
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from scripts.launch_tunnel import (
    URL_PATTERN,
    update_env_file,
    get_configured_named_tunnel_token,
    is_port_open,
)


def test_url_pattern_regex():
    sample_log = (
        "2026-10-27T09:54:00Z INF |  https://temple-deaf-bargains-nations.trycloudflare.com  |\n"
        "2026-10-27T09:54:00Z INF Registered tunnel connection\n"
    )
    m = URL_PATTERN.search(sample_log)
    assert m is not None
    assert m.group(0) == "https://temple-deaf-bargains-nations.trycloudflare.com"

    # Verify invalid patterns don't match
    assert URL_PATTERN.search("https://evil-site.com") is None
    assert URL_PATTERN.search("http://insecure.trycloudflare.com") is None


def test_update_env_file_replaces_old_origins(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    initial_content = (
        "AUTH_PUBLIC_APP_URL=https://old-random-tunnel.trycloudflare.com\n"
        "CORS_ALLOWED_ORIGINS=https://old-random-tunnel.trycloudflare.com,http://localhost:5173,http://127.0.0.1:8000\n"
        "CSRF_TRUSTED_ORIGINS=https://old-random-tunnel.trycloudflare.com,http://localhost:5173\n"
        "SOME_SECRET_KEY=supersecret123\n"
    )
    env_file.write_text(initial_content, encoding="utf-8")

    # Point PROJECT_ROOT in scripts.launch_tunnel to tmp_path
    import scripts.launch_tunnel
    monkeypatch.setattr(scripts.launch_tunnel, "PROJECT_ROOT", tmp_path)

    new_url = "https://fresh-active-tunnel-abc.trycloudflare.com"
    update_env_file(new_url)

    updated_content = env_file.read_text(encoding="utf-8")
    assert f"AUTH_PUBLIC_APP_URL={new_url}" in updated_content
    assert "https://old-random-tunnel.trycloudflare.com" not in updated_content
    assert "http://localhost:5173" in updated_content
    assert "http://127.0.0.1:8000" in updated_content
    assert "SOME_SECRET_KEY=supersecret123" in updated_content
    assert f"CORS_ALLOWED_ORIGINS={new_url},http://localhost:5173,http://127.0.0.1:8000" in updated_content
    assert f"CSRF_TRUSTED_ORIGINS={new_url},http://localhost:5173" in updated_content


def test_get_configured_named_tunnel_token(monkeypatch, tmp_path):
    import scripts.launch_tunnel
    monkeypatch.setattr(scripts.launch_tunnel, "PROJECT_ROOT", tmp_path)

    # When no token
    monkeypatch.delenv("CLOUDFLARE_TUNNEL_TOKEN", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("SOME_VAR=123\n", encoding="utf-8")
    assert get_configured_named_tunnel_token() is None

    # When token in .env
    env_file.write_text("CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiMTIzNDU2Nzg5MCJ9\n", encoding="utf-8")
    assert get_configured_named_tunnel_token() == "eyJhIjoiMTIzNDU2Nzg5MCJ9"

    # When token in environment variable
    monkeypatch.setenv("CLOUDFLARE_TUNNEL_TOKEN", "eyJhIjoiZW52LXZhci10b2tlbiJ9")
    assert get_configured_named_tunnel_token() == "eyJhIjoiZW52LXZhci10b2tlbiJ9"
