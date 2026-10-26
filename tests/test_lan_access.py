"""
Tests for LAN / Local Development Network Access and Security in SuchnaSetu AI.
Verifies:
- Authorized LAN origins (RFC1918 private IPs on port 5173/8000/3000) are accepted for CORS and CSRF in development.
- Untrusted public internet origins are strictly rejected with HTTP 403.
- Private network client IPs (e.g. 192.168.x.x) receive dev quota policy during local dev, but strict 10/10min quota in production.
- Production environment strictly blocks unauthorized origins.
"""

import pytest
from starlette.testclient import TestClient
from notice2action.api.server import app
from notice2action.config import config
from notice2action.auth.auth_service import auth_service
from notice2action.storage.db import get_db

client = TestClient(app, base_url="http://127.0.0.1:8000")


def test_lan_cors_preflight_options():
    """OPTIONS preflight request from a LAN origin (e.g. phone on 192.168.1.5:5173) receives valid CORS headers."""
    resp = client.options(
        "/api/analyze",
        headers={
            "Origin": "http://192.168.1.5:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://192.168.1.5:5173"
    assert resp.headers.get("access-control-allow-credentials") == "true"


def test_lan_post_request_allowed_in_dev(monkeypatch):
    """POST /api/analyze request carrying LAN Origin header succeeds without CSRF rejection in development."""
    monkeypatch.setattr(config, "app_env", "development")
    
    resp = client.post(
        "/api/analyze",
        json={"notice_text": "Public recruitment notice for Junior Engineer. Apply by 2026-11-30."},
        headers={
            "Origin": "http://192.168.1.5:5173",
            "Host": "192.168.1.5:8000",
        },
    )
    # Must succeed (HTTP 200), NOT get blocked by CSRF (HTTP 403)
    assert resp.status_code == 200
    data = resp.json()
    assert "structured_notice" in data
    assert "checklist_en" in data
    assert "six_core_fields" in data


def test_untrusted_public_origin_rejected_with_403(monkeypatch):
    """POST /api/analyze carrying a public internet or malicious origin is blocked with HTTP 403."""
    monkeypatch.setattr(config, "app_env", "development")

    resp = client.post(
        "/api/analyze",
        json={"notice_text": "Sample text"},
        headers={
            "Origin": "https://malicious-public-site.com",
            "Host": "192.168.1.5:8000",
        },
    )
    assert resp.status_code == 403
    assert "untrusted request origin" in resp.json()["detail"].lower()


def test_public_ip_origin_rejected_with_403(monkeypatch):
    """POST /api/analyze carrying a public non-RFC1918 IP origin is blocked with HTTP 403."""
    monkeypatch.setattr(config, "app_env", "development")

    resp = client.post(
        "/api/analyze",
        json={"notice_text": "Sample text"},
        headers={
            "Origin": "http://93.184.216.34:5173",
            "Host": "192.168.1.5:8000",
        },
    )
    assert resp.status_code == 403
    assert "untrusted request origin" in resp.json()["detail"].lower()


def test_lan_client_ip_dev_quota_policy(monkeypatch):
    """A phone on Wi-Fi (e.g. 192.168.1.105) receives dev quota policy during local development."""
    monkeypatch.setattr(config, "app_env", "development")
    monkeypatch.setattr(config, "dev_unlimited_guest_quota", True)

    phone_ip = "192.168.1.105"
    allowed, remaining = auth_service.check_guest_rate_limit(phone_ip, increment=True)
    assert allowed is True
    assert remaining == 999


def test_lan_client_ip_production_quota_enforcement(monkeypatch):
    """In production mode, LAN client IPs are strictly subject to standard 10/10min guest rate limits."""
    monkeypatch.setattr(config, "app_env", "production")
    monkeypatch.setattr(config, "dev_unlimited_guest_quota", False)

    phone_ip = "192.168.1.105"
    db = get_db()
    with db.get_connection() as conn:
        conn.execute("DELETE FROM rate_limits WHERE key = ?", (f"guest_limit:{phone_ip}",))

    for i in range(10):
        allowed, remaining = auth_service.check_guest_rate_limit(phone_ip, increment=True)
        assert allowed is True
        assert remaining == (9 - i)

    # 11th request must be rejected
    allowed_11, remaining_11 = auth_service.check_guest_rate_limit(phone_ip, increment=True)
    assert allowed_11 is False
    assert remaining_11 == 0


def test_lan_ocr_request_with_lan_origin(monkeypatch):
    """POST /api/ocr succeeds when submitted from a LAN origin (e.g. phone photo upload)."""
    from PIL import Image
    import io

    monkeypatch.setattr(config, "app_env", "development")

    img = Image.new("RGB", (300, 80), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    resp = client.post(
        "/api/ocr",
        files={"file": ("phone_upload.png", buf.getvalue(), "image/png")},
        data={"target_lang": "eng"},
        headers={
            "Origin": "http://192.168.1.5:5173",
            "Host": "192.168.1.5:8000",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "confidence_score" in data
    assert "line_count" in data
