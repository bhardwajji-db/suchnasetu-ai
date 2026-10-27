"""
SuchnaSetu AI — Local Image Upload & CSRF Origin Protection Tests
Validates:
1. Local frontend origin 'http://127.0.0.1:8000' is trusted for image uploads and state-changing endpoints.
2. Public Cloudflare Tunnel origin is trusted.
3. Untrusted / spoofed origins (e.g. attacker sites) are rejected with 403 Forbidden.
4. Referer-based origin validation acts as defense-in-depth when Origin header is omitted.
5. Auth endpoints (login/register) respect origin checks and cookie security attributes.
"""

import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.config import config
from notice2action.api.auth_routes import _is_request_https


@pytest.fixture
def synthetic_image_bytes():
    """Generates a small valid PNG in memory."""
    img = Image.new("RGB", (120, 50), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def test_cors_origins_includes_exact_local_origin():
    """Verify get_cors_origins explicitly includes the local loopback backend origin."""
    trusted = config.get_cors_origins()
    assert "http://127.0.0.1:8000" in trusted, f"http://127.0.0.1:8000 missing from trusted origins: {trusted}"


def test_local_upload_trusted_origin_allowed(synthetic_image_bytes):
    """Verify image upload succeeds when sent with Origin: http://127.0.0.1:8000."""
    client = TestClient(app)
    headers = {"Origin": "http://127.0.0.1:8000"}
    files = {"file": ("test_notice.png", io.BytesIO(synthetic_image_bytes), "image/png")}

    resp = client.post("/api/ingest/upload", headers=headers, files=files)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("source_type") == "image"
    assert data.get("filename") == "test_notice.png"


def test_public_tunnel_origin_allowed(synthetic_image_bytes):
    """Verify image upload succeeds when sent from the configured public app origin."""
    client = TestClient(app)
    headers = {"Origin": config.auth_public_app_url.rstrip("/")}
    files = {"file": ("tunnel_notice.png", io.BytesIO(synthetic_image_bytes), "image/png")}

    resp = client.post("/api/ingest/upload", headers=headers, files=files)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


def test_untrusted_origin_rejected_with_csrf_error(synthetic_image_bytes):
    """Verify untrusted origin is blocked with 403 CSRF verification failed."""
    client = TestClient(app)
    headers = {"Origin": "https://malicious-cross-origin.com"}
    files = {"file": ("exploit.png", io.BytesIO(synthetic_image_bytes), "image/png")}

    resp = client.post("/api/ingest/upload", headers=headers, files=files)
    assert resp.status_code == 403
    data = resp.json()
    assert "Untrusted request origin / CSRF verification failed." in data.get("detail", "")


def test_untrusted_referer_rejected(synthetic_image_bytes):
    """Verify request with untrusted Referer and no Origin is blocked."""
    client = TestClient(app)
    headers = {"Referer": "https://malicious-phishing.com/page"}
    files = {"file": ("phish.png", io.BytesIO(synthetic_image_bytes), "image/png")}

    resp = client.post("/api/ingest/upload", headers=headers, files=files)
    assert resp.status_code == 403
    data = resp.json()
    assert "Untrusted request origin / CSRF verification failed." in data.get("detail", "")


def test_trusted_referer_allowed(synthetic_image_bytes):
    """Verify request with trusted Referer and no Origin succeeds."""
    client = TestClient(app)
    headers = {"Referer": "http://127.0.0.1:8000/workspace"}
    files = {"file": ("workspace.png", io.BytesIO(synthetic_image_bytes), "image/png")}

    resp = client.post("/api/ingest/upload", headers=headers, files=files)
    assert resp.status_code == 200


def test_auth_login_untrusted_origin_rejected():
    """Verify login from untrusted origin is blocked by CSRF protection with 403."""
    client = TestClient(app)
    headers = {"Origin": "https://evil-hacker.com"}
    payload = {"email": "test@example.com", "password": "SamplePassword123!"}

    resp = client.post("/api/auth/login", headers=headers, json=payload)
    assert resp.status_code == 403
    assert "Untrusted request origin / CSRF verification failed." in resp.json().get("detail", "")


def test_auth_login_trusted_origin_passes_csrf():
    """Verify login from trusted local origin reaches auth handler (not blocked by CSRF)."""
    client = TestClient(app)
    headers = {"Origin": "http://127.0.0.1:8000"}
    payload = {"email": "nonexistent@example.com", "password": "InvalidPassword123!"}

    resp = client.post("/api/auth/login", headers=headers, json=payload)
    # Origin verification passes, so it should reach authentication logic and return 401 Unauthorized
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json().get("detail", "")


def test_is_request_https_logic():
    """Verify HTTPS detection distinguishes direct HTTP, trusted reverse-proxy HTTPS, and local origins."""
    class MockRequest:
        def __init__(self, scheme="http", host="127.0.0.1", headers=None):
            self.url = type("URL", (), {"scheme": scheme})()
            self.client = type("Client", (), {"host": host})()
            self.headers = headers or {}

    # Direct HTTPS -> True
    req_https = MockRequest(scheme="https")
    assert _is_request_https(req_https) is True

    # Direct plain HTTP from local -> False
    req_http = MockRequest(scheme="http", host="127.0.0.1", headers={"Origin": "http://127.0.0.1:8000"})
    assert _is_request_https(req_http) is False

    # Trusted proxy with X-Forwarded-Proto: https -> True
    req_proxy_https = MockRequest(
        scheme="http",
        host="127.0.0.1",
        headers={"X-Forwarded-Proto": "https"}
    )
    assert _is_request_https(req_proxy_https) is True

    # Untrusted proxy with spoofed X-Forwarded-Proto: https -> False
    req_untrusted_proxy = MockRequest(
        scheme="http",
        host="192.168.1.100",
        headers={"X-Forwarded-Proto": "https"}
    )
    assert _is_request_https(req_untrusted_proxy) is False
