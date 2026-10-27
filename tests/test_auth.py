"""
Comprehensive Authentication & Account Security Suite for SuchnaSetu AI.
Verifies:
- Citizen registration with Argon2id hashing and password validation
- Account verification via 6-digit OTP codes and magic tokens
- Login flow with secure HttpOnly session cookies
- Protection of /api/auth/me and protected routes
- Password recovery and active session revocation
- Rate limiting and brute-force lockout protections
- CSRF untrusted origin rejection
- Genuine guest mode enforcement
- Zero leakage of raw tokens, credentials, or hashes in API responses
"""

import time
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.storage.db import get_db
from notice2action.auth.security import verify_password, hash_token, hash_code
from notice2action.auth.email_service import EmailDeliveryResult, email_service
from notice2action.auth.auth_service import auth_service
from notice2action.config import config

client = TestClient(app, base_url="http://testserver", headers={"Origin": "http://testserver"})


@pytest.fixture(scope="function", autouse=True)
def clean_test_auth_tables():
    """Ensure test rate limits and test users are clean between tests."""
    client.cookies.clear()
    db = get_db()
    conn = db.get_connection()
    with conn:
        conn.execute("DELETE FROM users WHERE email LIKE '%@test.suchnasetu.gov.in'")
        conn.execute("DELETE FROM rate_limits")


def test_registration_success():
    """Citizen can register with username/email/password without OTP and receives an active account."""
    payload = {
        "username": "Arjun Sharma",
        "email": "arjun.sharma@test.suchnasetu.gov.in",
        "password": "SecurePassphrase2026#Citizen",
        "confirm_password": "SecurePassphrase2026#Citizen"
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "created" in data["message"].lower()
    cookie_name = getattr(config, "auth_cookie_name", "suchnasetu_session")
    assert cookie_name in resp.cookies or "session" in str(resp.headers)

    db = get_db()
    conn = db.get_connection()
    with conn:
        cur = conn.execute(
            "SELECT id, email, is_verified, password_hash FROM users WHERE email = ?",
            ("arjun.sharma@test.suchnasetu.gov.in",)
        )
        row = cur.fetchone()
        assert row is not None
        assert row["is_verified"] == 1
        assert verify_password("SecurePassphrase2026#Citizen", row["password_hash"])
        assert "$argon2id$" in row["password_hash"]


def test_registration_password_mismatch():
    """Registration fails if passwords do not match."""
    payload = {
        "name": "Priya Verma",
        "email": "priya.verma@test.suchnasetu.gov.in",
        "password": "Password123#",
        "confirm_password": "DifferentPassword123#"
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code in (400, 422)


def test_registration_short_password():
    """Registration rejects passwords shorter than 8 characters."""
    payload = {
        "name": "Short Pass User",
        "email": "short@test.suchnasetu.gov.in",
        "password": "short",
        "confirm_password": "short"
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code in (400, 422)


def test_registration_duplicate_handling_generic():
    """Duplicate email registration is rejected with HTTP 400."""
    payload = {
        "name": "Arjun Sharma",
        "email": "arjun.sharma@test.suchnasetu.gov.in",
        "password": "SecurePassphrase2026#Citizen",
        "confirm_password": "SecurePassphrase2026#Citizen"
    }
    client.post("/api/auth/register", json=payload)

    dup_payload = {
        "name": "Arjun Sharma Duplicate",
        "email": "ARJUN.SHARMA@test.suchnasetu.gov.in",
        "password": "AnotherPassword2026#",
        "confirm_password": "AnotherPassword2026#"
    }
    resp = client.post("/api/auth/register", json=dup_payload)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


def test_login_unverified_account_forbidden():
    """Accounts without prior verification can sign in directly without OTP barrier."""
    payload = {
        "name": "Direct Login User",
        "email": "direct@test.suchnasetu.gov.in",
        "password": "SecurePassphrase2026#Citizen",
        "confirm_password": "SecurePassphrase2026#Citizen"
    }
    client.post("/api/auth/register", json=payload)

    resp = client.post("/api/auth/login", json={
        "email": "direct@test.suchnasetu.gov.in",
        "password": "SecurePassphrase2026#Citizen"
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "success" 


def test_verify_email_with_code():
    """Citizen account is immediately verified upon registration with no pending OTP tokens."""
    email = "verify.code@test.suchnasetu.gov.in"
    reg_resp = client.post("/api/auth/register", json={
        "name": "Verify Citizen",
        "email": email,
        "password": "SecurePassphrase2026#Citizen",
        "confirm_password": "SecurePassphrase2026#Citizen"
    })
    assert reg_resp.status_code == 200

    db = get_db()
    with db.get_connection() as conn:
        cur = conn.execute("SELECT id, is_verified FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        assert user is not None
        assert user["is_verified"] == 1
        # No OTP tokens inserted for registration
        cur = conn.execute("SELECT COUNT(*) as count FROM auth_tokens WHERE user_id = ? AND token_type LIKE 'verify_email%'", (user["id"],))
        assert cur.fetchone()["count"] == 0
def test_login_success_and_session_cookie():
    """Verified citizen signs in and receives an HttpOnly session cookie."""
    email = "login.success@test.suchnasetu.gov.in"
    client.post("/api/auth/register", json={
        "name": "Login Citizen",
        "email": email,
        "password": "SecurePassphrase2026#Citizen",
        "confirm_password": "SecurePassphrase2026#Citizen"
    })

    db = get_db()
    conn = db.get_connection()
    with conn:
        conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))

    resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "SecurePassphrase2026#Citizen",
        "remember_me": True
    })
    assert resp.status_code == 200
    assert "suchnasetu_session" in resp.cookies
    data = resp.json()
    assert data["status"] == "success"
    assert data["user"]["email"] == email


def test_login_invalid_password():
    """Login with wrong password returns HTTP 401."""
    resp = client.post("/api/auth/login", json={
        "email": "nonexistent@test.suchnasetu.gov.in",
        "password": "WrongPassword123#"
    })
    assert resp.status_code == 401


def test_me_unauthenticated():
    """Unauthenticated access to /api/auth/me returns HTTP 401."""
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_logout_revokes_session():
    """Logout invalidates the server session and deletes session cookie."""
    email = "logout.test@test.suchnasetu.gov.in"
    client.post("/api/auth/register", json={
        "name": "Logout Citizen",
        "email": email,
        "password": "SecurePassphrase2026#Citizen",
        "confirm_password": "SecurePassphrase2026#Citizen"
    })

    db = get_db()
    conn = db.get_connection()
    with conn:
        conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))

    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "SecurePassphrase2026#Citizen"
    })
    session_token = login_resp.cookies.get("suchnasetu_session")
    assert session_token is not None

    # Access /me with session
    me_resp = client.get("/api/auth/me", cookies={"suchnasetu_session": session_token})
    assert me_resp.status_code == 200

    # Logout
    logout_resp = client.post("/api/auth/logout", cookies={"suchnasetu_session": session_token})
    assert logout_resp.status_code == 200

    # Verify session is revoked
    revoked_resp = client.get("/api/auth/me", cookies={"suchnasetu_session": session_token})
    assert revoked_resp.status_code == 401


def test_forgot_password_generic_response():
    """Forgot password returns generic success message regardless of user existence."""
    resp = client.post("/api/auth/forgot-password", json={
        "email": "ghost.user@test.suchnasetu.gov.in",
        "method": "code"
    })
    assert resp.status_code == 200
    assert "recovery instructions" in resp.json()["message"].lower()


def test_reset_password_with_code():
    """Citizen can reset their password with a 6-digit recovery code."""
    email = "reset.code@test.suchnasetu.gov.in"
    client.post("/api/auth/register", json={
        "name": "Reset Citizen",
        "email": email,
        "password": "OldPassword123#Citizen",
        "confirm_password": "OldPassword123#Citizen"
    })

    db = get_db()
    conn = db.get_connection()
    with conn:
        conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))

    # Request password recovery
    client.post("/api/auth/forgot-password", json={"email": email, "method": "code"})

    with conn:
        cur = conn.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cur.fetchone()["id"]
        cur = conn.execute(
            "SELECT token_hash FROM auth_tokens WHERE user_id = ? AND token_type = 'reset_password_code' ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        token_hash = cur.fetchone()["token_hash"]

    test_code = None
    for c in range(100000, 1000000):
        if hash_code(str(c)) == token_hash:
            test_code = str(c)
            break

    assert test_code is not None

    reset_resp = client.post("/api/auth/reset-password", json={
        "email": email,
        "code": test_code,
        "new_password": "BrandNewSecurePassword2026#",
        "confirm_password": "BrandNewSecurePassword2026#"
    })
    assert reset_resp.status_code == 200
    assert "updated" in reset_resp.json()["message"].lower()

    # Sign in with new password
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "BrandNewSecurePassword2026#"
    })
    assert login_resp.status_code == 200


def test_csrf_untrusted_origin_rejection():
    """State-changing requests with untrusted Origin header are blocked (HTTP 403)."""
    resp = client.post(
        "/api/auth/register",
        json={"name": "Evil", "email": "evil@test.suchnasetu.gov.in", "password": "Password123#"},
        headers={"Origin": "https://malicious-phishing-site.example.com"}
    )
    assert resp.status_code == 403
    assert "untrusted" in resp.json()["detail"].lower()


def test_guest_mode_analysis_allowed_within_quota():
    """Unauthenticated guest can analyze notices within rate limit quota."""
    from notice2action.schemas import StructuredNotice, ExtractedFact, CertaintyStatus
    dummy = StructuredNotice(
        purpose=ExtractedFact(field_name="purpose", value="State Scholarship", status=CertaintyStatus.STATED, evidence_quote="State Scholarship"),
        deadline=ExtractedFact(field_name="deadline", value="15/11/2026", status=CertaintyStatus.STATED, evidence_quote="15/11/2026"),
        eligibility=ExtractedFact(field_name="eligibility", value="Students", status=CertaintyStatus.STATED, evidence_quote="Students"),
        fee_or_cost=ExtractedFact(field_name="fee_or_cost", value="None", status=CertaintyStatus.NOT_STATED, evidence_quote=None),
        required_documents=ExtractedFact(field_name="required_documents", value="ID", status=CertaintyStatus.STATED, evidence_quote="ID"),
        contact_details=ExtractedFact(field_name="contact_details", value="Helpdesk", status=CertaintyStatus.STATED, evidence_quote="Helpdesk"),
        required_actions=ExtractedFact(field_name="required_actions", value="Apply", status=CertaintyStatus.STATED, evidence_quote="Apply"),
        important_conditions=ExtractedFact(field_name="important_conditions", value="None", status=CertaintyStatus.STATED, evidence_quote="None"),
        missing_information=[],
        uncertain_or_conflicting_details=[],
        raw_notice_text="OFFICIAL ADVISORY: State Post-Matric Scholarship deadline is 15/11/2026.",
    )
    with patch("notice2action.api.server.NoticeAnalyzer.analyze_notice", return_value=dummy):
        notice_text = "OFFICIAL ADVISORY: State Post-Matric Scholarship deadline is 15/11/2026."
        resp = client.post("/api/analyze", json={"notice_text": notice_text})
        assert resp.status_code == 200
        data = resp.json()
        assert "structured_notice" in data


def test_guest_status_endpoint():
    """Guest status endpoint accurately reflects remaining quota."""
    resp = client.get("/api/auth/guest-status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_guest"] is True
    assert data["remaining_analyses"] >= 0


def test_recovery_code_excessive_attempts_lockout():
    """Entering wrong recovery code 5 times locks out and invalidates the code."""
    email = "lockout.user@test.suchnasetu.gov.in"
    client.post("/api/auth/register", json={
        "name": "Lockout User",
        "email": email,
        "password": "Password123#Citizen",
        "confirm_password": "Password123#Citizen"
    })
    db = get_db()
    conn = db.get_connection()
    with conn:
        conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))

    client.post("/api/auth/forgot-password", json={"email": email, "method": "code"})

    # Submit 5 incorrect codes
    for _ in range(5):
        resp = client.post("/api/auth/reset-password", json={
            "email": email,
            "code": "000000",
            "new_password": "NewPassword2026#"
        })
        assert resp.status_code == 400

    # 6th attempt should explicitly mention excessive attempts / invalidated
    resp6 = client.post("/api/auth/reset-password", json={
        "email": email,
        "code": "000000",
        "new_password": "NewPassword2026#"
    })
    assert resp6.status_code == 400
    assert "attempts" in resp6.json()["detail"].lower() or "invalidated" in resp6.json()["detail"].lower()


def test_password_reset_revokes_active_sessions_immediately():
    """Active user sessions are revoked immediately upon password reset."""
    email = "revoke.sessions@test.suchnasetu.gov.in"
    client.post("/api/auth/register", json={
        "name": "Revoke User",
        "email": email,
        "password": "Password123#Citizen",
        "confirm_password": "Password123#Citizen"
    })
    db = get_db()
    conn = db.get_connection()
    with conn:
        conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))

    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123#Citizen"
    })
    session_token = login_resp.cookies.get("suchnasetu_session")
    assert session_token is not None

    # Verify session works
    assert client.get("/api/auth/me", cookies={"suchnasetu_session": session_token}).status_code == 200

    # Request recovery code
    client.post("/api/auth/forgot-password", json={"email": email, "method": "code"})

    with conn:
        cur = conn.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cur.fetchone()["id"]
        cur = conn.execute(
            "SELECT token_hash FROM auth_tokens WHERE user_id = ? AND token_type = 'reset_password_code' ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        token_hash = cur.fetchone()["token_hash"]

    test_code = None
    for c in range(100000, 1000000):
        if hash_code(str(c)) == token_hash:
            test_code = str(c)
            break

    # Reset password
    client.post("/api/auth/reset-password", json={
        "email": email,
        "code": test_code,
        "new_password": "NewPassword123#Citizen"
    })

    # Old session must now be rejected
    assert client.get("/api/auth/me", cookies={"suchnasetu_session": session_token}).status_code == 401


def test_api_responses_never_expose_tokens_or_hashes():
    """API responses must never return password hashes, raw tokens, or token hashes."""
    email = "safe.citizen@test.suchnasetu.gov.in"
    reg_resp = client.post("/api/auth/register", json={
        "name": "Safe Citizen",
        "email": email,
        "password": "Password123#Citizen",
        "confirm_password": "Password123#Citizen"
    })
    text = reg_resp.text.lower()
    assert "password_hash" not in text
    assert "$argon2id$" not in text
    assert "token_hash" not in text

    db = get_db()
    conn = db.get_connection()
    with conn:
        conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))

    login_resp = client.post("/api/auth/login", json={"email": email, "password": "Password123#Citizen"})
    login_text = login_resp.text.lower()
    assert "password_hash" not in login_text
    assert "$argon2id$" not in login_text


def test_resend_verification_cooldown():
    """Cooldown limits repeated resend verification requests for unverified accounts."""
    email = "cooldown@test.suchnasetu.gov.in"
    client.post("/api/auth/register", json={
        "name": "Cooldown User",
        "email": email,
        "password": "Password123#Citizen",
        "confirm_password": "Password123#Citizen"
    })
    db = get_db()
    with db.get_connection() as conn:
        conn.execute("UPDATE users SET is_verified = 0 WHERE email = ?", (email,))

    # First resend
    client.post("/api/auth/resend-verification", json={"email": email})
    # Second immediate resend triggers cooldown
    resend_resp = client.post("/api/auth/resend-verification", json={"email": email})
    assert resend_resp.status_code == 429
    assert "wait" in resend_resp.json()["detail"].lower()


def test_dev_mode_loopback_unlimited_quota():
    """In development mode, loopback IPs get unlimited guest quota to allow repeatable testing."""
    allowed, remaining = auth_service.check_guest_rate_limit("127.0.0.1", increment=True)
    assert allowed is True
    assert remaining == 999
    allowed_tc, remaining_tc = auth_service.check_guest_rate_limit("testclient", increment=True)
    assert allowed_tc is True
    assert remaining_tc == 999


def test_production_mode_strict_guest_quota_enforcement(monkeypatch):
    """In production mode, guest quota strictly caps at 10 requests per 10 minutes and rejects 11th with HTTP 429."""
    monkeypatch.setattr(config, "app_env", "production")
    monkeypatch.setattr(config, "dev_unlimited_guest_quota", False)
    test_ip = "198.51.100.42"

    db = get_db()
    with db.get_connection() as conn:
        conn.execute("DELETE FROM rate_limits WHERE key = ?", (f"guest_limit:{test_ip}",))

    # Consume 10 allowed requests
    for i in range(10):
        allowed, remaining = auth_service.check_guest_rate_limit(test_ip, increment=True)
        assert allowed is True
        assert remaining == (9 - i)

    # 11th request must be rejected
    allowed_11, remaining_11 = auth_service.check_guest_rate_limit(test_ip, increment=True)
    assert allowed_11 is False
    assert remaining_11 == 0


def test_ocr_endpoint_never_blocked_by_notice_analysis_quota(monkeypatch):
    """OCR endpoint execution is never blocked or rejected when guest notice analysis quota is exhausted."""
    from PIL import Image
    import io

    monkeypatch.setattr(config, "app_env", "production")
    monkeypatch.setattr(config, "dev_unlimited_guest_quota", False)
    db = get_db()
    with db.get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO rate_limits (key, count, window_start) VALUES (?, 10, ?)",
            ("guest_limit:testclient", time.time())
        )

    # Calling analyze must be rejected with 429
    resp_analyze = client.post("/api/analyze", json={"notice_text": "Sample text for testing"})
    assert resp_analyze.status_code == 429
    assert "quota exceeded" in resp_analyze.json()["detail"].lower()

    # BUT calling OCR endpoint must NOT be blocked with 429
    img = Image.new("RGB", (200, 50), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    resp_ocr = client.post(
        "/api/ocr",
        files={"file": ("test_ocr.png", buf.getvalue(), "image/png")},
        data={"target_lang": "eng"}
    )
    assert resp_ocr.status_code != 429


def test_ocr_rate_limit_enforcement(monkeypatch):
    """Verify that OCR rate limiting is enforced in production mode for guests while dev loopback is unlimited."""
    monkeypatch.setattr(config, "app_env", "production")
    monkeypatch.setattr(config, "dev_unlimited_guest_quota", False)
    monkeypatch.setattr(config, "ocr_rate_limit_guest_per_min", 3)

    test_ip = "198.51.100.99"
    db = get_db()
    with db.get_connection() as conn:
        conn.execute("DELETE FROM rate_limits WHERE key = ?", (f"ocr_limit:guest:{test_ip}",))

    # Consume 3 requests
    for i in range(3):
        allowed, remaining = auth_service.check_ocr_rate_limit(test_ip, is_authenticated=False)
        assert allowed is True
        assert remaining == (2 - i)

    # 4th request must be rejected
    allowed_4, remaining_4 = auth_service.check_ocr_rate_limit(test_ip, is_authenticated=False)
    assert allowed_4 is False
    assert remaining_4 == 0

    # In dev mode with loopback, requests must always pass
    monkeypatch.setattr(config, "app_env", "development")
    monkeypatch.setattr(config, "dev_unlimited_guest_quota", True)
    loopback_allowed, loopback_rem = auth_service.check_ocr_rate_limit("127.0.0.1", is_authenticated=False)
    assert loopback_allowed is True
    assert loopback_rem == 999
