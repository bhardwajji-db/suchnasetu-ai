"""
Security Audit Remediation Verification Suite.
Validates authentication enforcement, cross-tenant isolation, CSRF protection,
and security headers for SochnaSetu AI.
"""

import pytest
from fastapi.testclient import TestClient
from notice2action.api.server import app
from notice2action.storage.db import get_db
from notice2action.auth.auth_service import auth_service


@pytest.fixture
def client():
    return TestClient(app, base_url="http://127.0.0.1:8000")


def test_unauthenticated_documents_endpoint_rejected_401(client):
    """Vulnerability Fix 1: Ensure unauthenticated requests to /api/documents are blocked with 401."""
    resp = client.get("/api/documents")
    assert resp.status_code == 401
    assert "Authentication required" in resp.json().get("detail", "")


def test_authenticated_documents_isolation(client):
    """Ensure authenticated users can only view their own documents, not the global database dump."""
    # Register/login a synthetic citizen test user
    email = "security_test_citizen@example.com"
    pwd = "SecPassword123!Safe"
    reg_resp = client.post("/api/auth/register", json={
        "email": email,
        "password": pwd,
        "name": "Security Test Citizen",
    }, headers={"Origin": "http://127.0.0.1:8000"})
    
    # Login to obtain session cookie
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": pwd,
    }, headers={"Origin": "http://127.0.0.1:8000"})
    assert login_resp.status_code == 200
    cookies = login_resp.cookies

    # Citizen with no saved notices gets an empty list, NOT the full documents dump
    docs_resp = client.get("/api/documents", cookies=cookies)
    assert docs_resp.status_code == 200
    data = docs_resp.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_csrf_cookie_missing_origin_referer_rejected_403(client):
    """Vulnerability Fix 2: State-changing requests with session cookies must present Origin or Referer."""
    # Set a session cookie and perform a POST with no Origin or Referer
    resp = client.post(
        "/api/workspace/clear",
        cookies={"notice2action_session": "synthetic_fake_session_token_123"},
    )
    assert resp.status_code == 403
    assert "Origin or Referer header required" in resp.json().get("detail", "")


def test_csrf_untrusted_origin_blocked_403(client):
    """CSRF: State-changing requests with untrusted origin are rejected with 403."""
    resp = client.post(
        "/api/workspace/clear",
        headers={"Origin": "https://malicious-attacker-website.com"},
    )
    assert resp.status_code == 403
    assert "Untrusted request origin" in resp.json().get("detail", "")


def test_csrf_trusted_origin_allowed(client):
    """CSRF: Requests from trusted origin succeed."""
    resp = client.post(
        "/api/workspace/clear",
        headers={"Origin": "http://127.0.0.1:8000"},
    )
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"


def test_workspace_isolation_across_users(client):
    """Vulnerability Fix 3: Workspaces must be isolated between distinct users/guests."""
    # User A session
    user_a_email = "user_a_isolated@example.com"
    client.post("/api/auth/register", json={
        "email": user_a_email,
        "password": "PasswordUserA123!",
        "name": "User A",
    }, headers={"Origin": "http://127.0.0.1:8000"})
    login_a = client.post("/api/auth/login", json={
        "email": user_a_email,
        "password": "PasswordUserA123!",
    }, headers={"Origin": "http://127.0.0.1:8000"})
    cookies_a = login_a.cookies

    # User B session
    user_b_email = "user_b_isolated@example.com"
    client.post("/api/auth/register", json={
        "email": user_b_email,
        "password": "PasswordUserB123!",
        "name": "User B",
    }, headers={"Origin": "http://127.0.0.1:8000"})
    login_b = client.post("/api/auth/login", json={
        "email": user_b_email,
        "password": "PasswordUserB123!",
    }, headers={"Origin": "http://127.0.0.1:8000"})
    cookies_b = login_b.cookies

    # User A clears their workspace and adds Notice A
    client.post("/api/workspace/clear", cookies=cookies_a, headers={"Origin": "http://127.0.0.1:8000"})
    add_a = client.post(
        "/api/workspace/notices",
        json={"text": "Notice A for User A only. Ref No: UA/2026/01.", "title": "Notice A"},
        cookies=cookies_a,
        headers={"Origin": "http://127.0.0.1:8000"},
    )
    assert add_a.status_code == 200

    # User B checks their workspace: should be EMPTY, never containing Notice A
    res_b = client.get("/api/workspace/notices", cookies=cookies_b)
    assert res_b.status_code == 200
    notices_b = res_b.json()
    assert all("Notice A" not in n.get("title", "") for n in notices_b)

    # User B adds Notice B
    add_b = client.post(
        "/api/workspace/notices",
        json={"text": "Notice B for User B only. Ref No: UB/2026/02.", "title": "Notice B"},
        cookies=cookies_b,
        headers={"Origin": "http://127.0.0.1:8000"},
    )
    assert add_b.status_code == 200

    # User A's workspace still only contains Notice A
    res_a = client.get("/api/workspace/notices", cookies=cookies_a)
    assert res_a.status_code == 200
    notices_a = res_a.json()
    assert len(notices_a) == 1
    assert notices_a[0]["title"] == "Notice A"

    # User B clears their workspace: User A's workspace is NOT touched
    client.post("/api/workspace/clear", cookies=cookies_b, headers={"Origin": "http://127.0.0.1:8000"})
    res_a_after = client.get("/api/workspace/notices", cookies=cookies_a)
    assert len(res_a_after.json()) == 1


def test_security_headers_present_on_all_responses(client):
    """Vulnerability Fix 6: Confirm security headers are emitted."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_sample_content_path_traversal_prevented(client):
    """Vulnerability Fix 5: Verify samples endpoint prevents path traversal."""
    resp = client.get("/api/samples/../../package.json")
    # Base name is extracted ('package.json') which is not in synthetic fixtures, so 404 is safely returned
    assert resp.status_code == 404
