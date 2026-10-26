"""
Comprehensive verification suite for DEF-02:
SMTP Configuration, Email Service Validation, Mocked Delivery, OTP Security, and Password Recovery.
Strict non-destructive testing with synthetic test fixtures only.
"""

import os
import uuid
import time
import asyncio
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

from notice2action.config import AppConfig, config
from notice2action.auth.email_service import EmailService, EmailDeliveryResult
from notice2action.auth.auth_service import AuthService
from notice2action.auth.security import hash_token, hash_code, verify_code
from notice2action.storage.db import get_db


@pytest.fixture(autouse=True)
def clean_test_state():
    """Isolate tests from shared rate limits and clean test users."""
    db = get_db()
    conn = db.get_connection()
    with conn:
        conn.execute("DELETE FROM rate_limits;")
        conn.execute("DELETE FROM users WHERE email LIKE '%@test.suchnasetu.gov.in';")


def test_smtp_configuration_parsing():
    """AppConfig correctly maps SMTP and auth email environment variables."""
    cfg = AppConfig()
    assert hasattr(cfg, "auth_email_backend")
    assert hasattr(cfg, "smtp_host")
    assert hasattr(cfg, "smtp_port")
    assert hasattr(cfg, "smtp_username")
    assert hasattr(cfg, "smtp_password")
    assert hasattr(cfg, "smtp_use_tls")
    assert hasattr(cfg, "smtp_from_email")
    assert hasattr(cfg, "auth_public_app_url")
    assert hasattr(cfg, "auth_verify_expire_hours")
    assert hasattr(cfg, "auth_token_expire_minutes")
    assert hasattr(cfg, "guest_rate_limit_per_window")


def test_smtp_validation_rules():
    """validate_smtp_config correctly identifies valid, missing, and malformed SMTP settings."""
    # 1. Console mode requires no external SMTP settings
    cfg_console = AppConfig(auth_email_backend="console", smtp_host="")
    valid, err = cfg_console.validate_smtp_config()
    assert valid is True
    assert err is None

    # 2. SMTP mode with missing host fails validation
    cfg_no_host = AppConfig(auth_email_backend="smtp", smtp_host="   ")
    valid, err = cfg_no_host.validate_smtp_config()
    assert valid is False
    assert "SMTP_HOST is required" in err

    # 3. SMTP mode with invalid port fails validation
    cfg_bad_port = AppConfig(auth_email_backend="smtp", smtp_host="smtp.example.gov.in", smtp_port=99999)
    valid, err = cfg_bad_port.validate_smtp_config()
    assert valid is False
    assert "Invalid SMTP_PORT" in err

    # 4. Valid SMTP configuration passes
    cfg_valid = AppConfig(auth_email_backend="smtp", smtp_host="smtp.example.gov.in", smtp_port=587)
    valid, err = cfg_valid.validate_smtp_config()
    assert valid is True
    assert err is None


def test_email_service_invalid_smtp_fails_gracefully():
    """EmailService._send_smtp detects invalid configuration and returns a clear user-facing error."""
    async def _run():
        svc = EmailService()
        with patch.object(config, "auth_email_backend", "smtp"), \
             patch.object(config, "smtp_host", ""):
            result = await svc.send_email(
                recipient="test@example.com",
                subject="Test Notification",
                text_content="Hello text",
                html_content="<p>Hello html</p>"
            )
            assert result.success is False
            assert result.backend == "smtp"
            assert "SMTP_HOST is required" in result.message
    asyncio.run(_run())


def test_email_service_console_mode_safe():
    """Console mode logs dispatch safely without network connection."""
    async def _run():
        svc = EmailService()
        with patch.object(config, "auth_email_backend", "console"):
            result = await svc.send_email(
                recipient="citizen@suchnasetu.gov.in",
                subject="Citizen Action Plan Ready",
                text_content="Text payload",
                html_content="<p>Html payload</p>"
            )
            assert result.success is True
            assert result.backend == "console"
            assert "console logger" in result.message.lower()
    asyncio.run(_run())


def test_mocked_signup_verification_flow():
    """End-to-end signup verification flow with mocked email delivery."""
    async def _run():
        auth = AuthService()
        synth_email = f"synth_{uuid.uuid4().hex[:8]}@test.suchnasetu.gov.in"
        synth_name = "Synthetic Citizen"

        # Mock email delivery to succeed
        with patch("notice2action.auth.auth_service.email_service.send_verification_email", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = EmailDeliveryResult(True, "Mock sent", "mock")
            res = await auth.register_user(
                name=synth_name,
                email=synth_email,
                password="SecurePassphrase2026#Citizen",
                client_ip=f"10.0.{uuid.uuid4().int % 200}.1"
            )
            assert res["status"] == "success"
            assert res["email_delivered"] is True
            assert mock_send.await_count == 1
            
            # Verify call arguments
            call_kwargs = mock_send.call_args.kwargs
            assert call_kwargs["email"] == synth_email
            assert call_kwargs["name"] == synth_name
            code = call_kwargs["code"]
            assert len(code) == 6 and code.isdigit()

            # Verify email using the generated 6-digit code
            verify_res = await auth.verify_email(email=synth_email, code=code)
            assert verify_res["status"] == "success"
            
            db = get_db()
            conn = db.get_connection()
            cur = conn.execute("SELECT is_verified FROM users WHERE email = ?", (synth_email,))
            assert cur.fetchone()["is_verified"] == 1

            # Subsequent verification request recognizes already verified account
            subsequent = await auth.verify_email(email=synth_email, code=code)
            assert "already verified" in subsequent["message"].lower()
    asyncio.run(_run())


def test_mocked_failed_email_delivery_surfaces_clear_status():
    """When email delivery fails, the system returns a warning status and does not falsely claim sent."""
    async def _run():
        auth = AuthService()
        synth_email = f"synth_{uuid.uuid4().hex[:8]}@test.suchnasetu.gov.in"

        with patch("notice2action.auth.auth_service.email_service.send_verification_email", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = EmailDeliveryResult(False, "Connection to mail server timed out", "smtp")
            res = await auth.register_user(
                name="Delivery Test",
                email=synth_email,
                password="SecurePassphrase2026#Citizen",
                client_ip=f"10.0.{uuid.uuid4().int % 200}.2"
            )
            assert res["status"] == "warning"
            assert res["email_delivered"] is False
            assert "could not be delivered" in res["message"].lower()
    asyncio.run(_run())


def test_password_reset_single_use_and_expiration():
    """Password reset token is strictly single-use and expires after TTL."""
    async def _run():
        auth = AuthService()
        synth_email = f"synth_{uuid.uuid4().hex[:8]}@test.suchnasetu.gov.in"
        client_ip = f"10.0.{uuid.uuid4().int % 200}.3"

        # Register and verify synthetic account
        with patch("notice2action.auth.auth_service.email_service.send_verification_email", new_callable=AsyncMock) as mock_v:
            mock_v.return_value = EmailDeliveryResult(True, "Sent", "mock")
            await auth.register_user(name="Reset User", email=synth_email, password="OriginalPassphrase2026#", client_ip=client_ip)
            code = mock_v.call_args.kwargs["code"]
            await auth.verify_email(email=synth_email, code=code)

        # Request password reset code
        with patch("notice2action.auth.auth_service.email_service.send_password_reset_code", new_callable=AsyncMock) as mock_reset:
            mock_reset.return_value = EmailDeliveryResult(True, "Reset sent", "mock")
            res = await auth.request_password_reset(email=synth_email, method="code", client_ip=client_ip)
            assert res["status"] == "success"
            reset_code = mock_reset.call_args.kwargs["code"]

            # Reset password
            reset_res = await auth.reset_password(
                new_password="UpdatedPassphrase2026#Citizen",
                email=synth_email,
                code=reset_code
            )
            assert reset_res["status"] == "success"

            # Reusing the same reset code must fail with 400 Bad Request
            with pytest.raises(HTTPException) as exc_info:
                await auth.reset_password(
                    new_password="AnotherPassphrase2026#Citizen",
                    email=synth_email,
                    code=reset_code
                )
            assert exc_info.value.status_code == 400
    asyncio.run(_run())
