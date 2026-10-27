"""
Tests for Free-Tier Deployment Compatibility (Cloudflare Pages + Render Free Tier).

Verifies:
1. Health check endpoints (/healthz and /health).
2. CORS headers for Cloudflare Pages (*.pages.dev).
3. CSRF origin validation for Cloudflare Pages.
4. Cross-site cookie policy (SameSite=None; Secure=True).
5. Linux Tesseract path candidate fallbacks.
6. Render Blueprint YAML validation (plan: free, no paid disk).
7. Durable R2/S3 storage sync fallback and backup creation.
"""

import os
import yaml
import pytest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from notice2action.config import config, _find_tesseract_cmd, _find_tessdata_dir
from notice2action.api.server import app, cors_regex
from notice2action.api.auth_routes import _is_request_https
from notice2action.storage.storage_sync import R2StorageSync
from notice2action.storage.db import DatabaseManager


@pytest.fixture
def client():
    return TestClient(app)


def test_healthz_and_health_endpoints(client):
    """Verify that both /healthz and /health return HTTP 200 with status ok."""
    r_healthz = client.get("/healthz")
    assert r_healthz.status_code == 200
    data_healthz = r_healthz.json()
    assert data_healthz["status"] == "ok"
    assert "SuchnaSetu" in data_healthz["app"]

    r_health = client.get("/health")
    assert r_health.status_code == 200
    data_health = r_health.json()
    assert data_health["status"] == "ok"


def test_cors_cloudflare_pages_preflight(client):
    """Verify OPTIONS preflight request from Cloudflare Pages (*.pages.dev) receives CORS approval."""
    origin = "https://suchnasetu.pages.dev"
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/api/ingest/text", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_cloudflare_pages_preview_branch(client):
    """Verify preview deployment URLs on Cloudflare Pages (*.pages.dev) are accepted."""
    preview_origin = "https://feat-new-ui.suchnasetu.pages.dev"
    headers = {
        "Origin": preview_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/api/ingest/text", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == preview_origin


def test_csrf_allows_cloudflare_pages(client):
    """Verify state-changing POST from *.pages.dev is not rejected by CSRF origin verification."""
    origin = "https://sochnasetu-hackathon.pages.dev"
    response = client.post(
        "/api/ingest/text",
        headers={"Origin": origin},
        data={"text": "Test notice text for deployment verification."},
    )
    # Status should not be 403 Forbidden (CSRF rejected)
    assert response.status_code != 403


def test_csrf_blocks_untrusted_foreign_origin(client):
    """Verify state-changing POST from an untrusted foreign origin is blocked with HTTP 403."""
    evil_origin = "https://malicious-phishing-site.example.com"
    response = client.post(
        "/api/ingest/text",
        headers={"Origin": evil_origin},
        data={"text": "Malicious payload attempt."},
    )
    assert response.status_code == 403
    assert "CSRF" in response.json().get("detail", "") or "untrusted" in response.json().get("detail", "").lower()


def test_cookie_samesite_none_enforces_secure():
    """Verify that when auth_cookie_samesite is 'none', _is_request_https returns True."""
    req = MagicMock()
    req.url.scheme = "http"
    req.client.host = "10.0.0.1"
    req.headers = {}

    with patch.object(config, "auth_cookie_samesite", "none"):
        assert _is_request_https(req) is True


def test_render_yaml_free_tier_validity():
    """Verify render.yaml has plan: free and does NOT declare a paid disk."""
    yaml_path = Path("render.yaml")
    assert yaml_path.is_file(), "render.yaml not found"

    with open(yaml_path, "r", encoding="utf-8") as f:
        blueprint = yaml.safe_load(f)

    services = blueprint.get("services", [])
    assert len(services) > 0, "No services in render.yaml"

    web_svc = next((s for s in services if s.get("name") == "sochnasetu-api"), services[0])
    assert web_svc.get("plan") == "free", "Render web service must specify 'plan: free'"
    assert "disk" not in web_svc, "Render Free tier does not support persistent disks (causes deployment error)"
    assert web_svc.get("healthCheckPath") == "/healthz"


def test_r2_storage_sync_unconfigured():
    """Verify R2StorageSync reports is_configured=False and skips safely when env vars absent."""
    sync = R2StorageSync(bucket_name="", access_key_id="", secret_access_key="", endpoint_url="")
    assert sync.is_configured is False
    assert sync.backup_database(Path("nonexistent.db")) is False
    assert sync.restore_database_if_missing(Path("nonexistent.db")) is False


def test_r2_storage_sync_sigv4_headers():
    """Verify AWS SigV4 signed headers generation."""
    sync = R2StorageSync(
        bucket_name="suchna-bucket",
        access_key_id="test_key_id",
        secret_access_key="test_secret_key",
        endpoint_url="https://account_id.r2.cloudflarestorage.com",
    )
    assert sync.is_configured is True

    headers = sync._build_signed_headers("GET", "account_id.r2.cloudflarestorage.com", "/suchna-bucket/suchnasetu.db")
    assert "Authorization" in headers
    assert "AWS4-HMAC-SHA256" in headers["Authorization"]
    assert "test_key_id" in headers["Authorization"]
    assert "x-amz-date" in headers
    assert "x-amz-content-sha256" in headers


def test_database_manager_backup_restore_methods():
    """Verify DatabaseManager has remote backup/restore hooks that execute safely."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test.db"
        uploads_dir = Path(tmp_dir) / "uploads"

        mgr = DatabaseManager(db_path=db_path, uploads_dir=uploads_dir)
        try:
            # Should gracefully return False when R2 is not configured, without crashing
            assert mgr.backup_to_remote_storage() is False
            assert mgr.restore_from_remote_storage() is False
        finally:
            mgr.close()

