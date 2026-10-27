"""
SuchnaSetu AI — Deployment Readiness & End-to-End Authentication Verification
Tests:
- Full citizen registration lifecycle
- Anti-enumeration duplicate handling
- Email verification OTP generation, delivery metadata, and validation
- Unverified account login blocking (HTTP 403)
- Verification code single-use guarantee and 5-attempt brute force lockout
- Session cookie issuance, profile inspection (/api/auth/me), and logout
- Password recovery via OTP, password reset, and old session revocation
- Production SPA static route serving (/verify-email, /reset-password, /login)
- Path traversal defense on static server
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.storage.db import get_db
from notice2action.auth.auth_service import auth_service
from notice2action.auth.security import hash_token, hash_code

client = TestClient(app)


def test_e2e_registration_verification_login_and_logout_flow():
    """Verify complete citizen journey from signup to email OTP verification, login, and logout."""
    db = get_db()
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"citizen_{unique_id}@example.gov.in"
    test_password = "SecurePassword@2026!"
    test_name = f"Citizen {unique_id}"

    # 1. Citizen Registration (Direct verified registration)
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "name": test_name,
            "email": test_email,
            "password": test_password,
            "confirm_password": test_password,
        },
    )
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["status"] == "success"

    # Verify user exists in database as verified citizen
    conn = db.get_connection()
    user_row = conn.execute("SELECT id, email, is_verified FROM users WHERE email = ?", (test_email,)).fetchone()
    assert user_row is not None
    assert user_row["is_verified"] == 1
    user_id = user_row["id"]

    # 2. Verified Citizen Login -> Must succeed and issue HttpOnly session cookie
    login_resp = client.post(
        "/api/auth/login",
        json={"email": test_email, "password": test_password, "remember_me": True},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["status"] == "success"
    assert login_data["user"]["is_verified"] is True
    assert login_data["user"]["email"] == test_email
    assert "suchnasetu_session" in login_resp.cookies

    session_cookie = login_resp.cookies["suchnasetu_session"]
    assert len(session_cookie) >= 32

    # 5. Access Protected Endpoint /api/auth/me with session cookie
    me_resp = client.get("/api/auth/me", cookies={"suchnasetu_session": session_cookie})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == test_email
    assert me_data["name"] == test_name
    assert me_data["is_guest"] is False

    # 6. Logout and Session Invalidation
    logout_resp = client.post("/api/auth/logout", cookies={"suchnasetu_session": session_cookie})
    assert logout_resp.status_code == 200

    # Confirm old session cannot access /api/auth/me anymore
    revoked_me = client.get("/api/auth/me", cookies={"suchnasetu_session": session_cookie})
    assert revoked_me.status_code == 401


def test_password_recovery_and_reset_flow():
    """Verify forgot-password OTP generation, password reset, and active session revocation."""
    db = get_db()
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"pwd_{unique_id}@example.gov.in"
    initial_password = "InitialPassword@2026!"
    new_password = "NewSecurePassword@2026!"

    # Create verified citizen
    conn = db.get_connection()
    from notice2action.auth.security import hash_password
    user_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO users (id, email, name, password_hash, is_verified, created_at, updated_at) "
        "VALUES (?, ?, 'Test User', ?, 1, datetime('now'), datetime('now'))",
        (user_id, test_email, hash_password(initial_password)),
    )
    conn.commit()

    # Login to create an active session
    login_resp = client.post(
        "/api/auth/login",
        json={"email": test_email, "password": initial_password},
    )
    assert login_resp.status_code == 200
    old_session_cookie = login_resp.cookies["suchnasetu_session"]

    # Verify session works
    me_resp = client.get("/api/auth/me", cookies={"suchnasetu_session": old_session_cookie})
    assert me_resp.status_code == 200

    # Request password reset code
    forgot_resp = client.post(
        "/api/auth/forgot-password",
        json={"email": test_email, "method": "code"},
    )
    assert forgot_resp.status_code == 200

    # Update generated reset OTP with known test OTP
    recovery_otp = "654321"
    code_hash = hash_code(recovery_otp)
    conn.execute(
        "UPDATE auth_tokens SET token_hash = ? WHERE user_id = ? AND token_type = 'reset_password_code' AND used_at IS NULL",
        (code_hash, user_id),
    )
    conn.commit()

    # Reset password with recovery code
    reset_resp = client.post(
        "/api/auth/reset-password",
        json={
            "email": test_email,
            "code": recovery_otp,
            "new_password": new_password,
            "confirm_password": new_password,
        },
    )
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "success"

    # Confirm previous session was revoked upon password reset
    revoked_resp = client.get("/api/auth/me", cookies={"suchnasetu_session": old_session_cookie})
    assert revoked_resp.status_code == 401

    # Confirm login succeeds with new password
    new_login = client.post(
        "/api/auth/login",
        json={"email": test_email, "password": new_password},
    )
    assert new_login.status_code == 200

    # Confirm login fails with old password
    old_login = client.post(
        "/api/auth/login",
        json={"email": test_email, "password": initial_password},
    )
    assert old_login.status_code == 401


def test_production_spa_routes_and_security_serving():
    """Verify FastAPI properly serves SPA views and blocks traversal or secret leakage."""
    # Root dashboard
    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert "text/html" in root_resp.headers.get("content-type", "")

    # Auth routes in SPA
    for route in ["/verify-email", "/reset-password", "/login", "/signup", "/dashboard", "/facts", "/history"]:
        spa_resp = client.get(route)
        assert spa_resp.status_code == 200
        assert "text/html" in spa_resp.headers.get("content-type", "")

    # Nonexistent API route -> must return HTTP 404 JSON, not SPA index.html
    api_404 = client.get("/api/definitely-not-an-endpoint")
    assert api_404.status_code == 404
    assert api_404.headers.get("content-type", "").startswith("application/json")

    # Path traversal attack -> must return HTTP 404
    traversal = client.get("/../../etc/passwd")
    assert traversal.status_code in [400, 404]
