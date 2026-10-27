"""
Authentication Service Layer for SuchnaSetu AI.
Handles user registration, verification, sessions, password recovery, rate limiting, and guest enforcement.
"""

import time
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status

from notice2action.storage.db import get_db
from notice2action.config import config
from notice2action.auth.security import (
    hash_password,
    verify_password,
    hash_token,
    hash_code,
    verify_code,
    generate_secure_token,
    generate_secure_code,
)
from notice2action.auth.email_service import email_service

logger = logging.getLogger("notice2action.auth.service")


def _mask_email(addr: str) -> str:
    if not addr or "@" not in addr:
        return "unknown"
    u, d = addr.split("@", 1)
    return (u[:2] + "***" if len(u) > 2 else "***") + "@" + d


def _is_dev_client_ip(client_ip: str) -> bool:
    """Returns True if client_ip is a local loopback or private network IP (RFC1918)."""
    if client_ip in ("127.0.0.1", "::1", "localhost", "testclient"):
        return True
    try:
        import ipaddress
        ip = ipaddress.ip_address(client_ip)
        return ip.is_private or ip.is_loopback
    except Exception:
        return False


class AuthService:
    """Core authentication, session, verification, and recovery business logic."""

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _expires_iso(hours: Optional[int] = None, minutes: Optional[int] = None) -> str:
        delta = timedelta(hours=hours or 0, minutes=minutes or 0)
        return (datetime.now(timezone.utc) + delta).isoformat()

    @staticmethod
    def _is_expired(expiry_iso: str) -> bool:
        try:
            exp = datetime.fromisoformat(expiry_iso)
            return datetime.now(timezone.utc) > exp
        except Exception:
            return True

    # --------------------------------------------------------------------------
    # Rate Limiting
    # --------------------------------------------------------------------------
    def check_rate_limit(self, key: str, max_requests: int, window_seconds: float) -> bool:
        """
        Token-bucket / sliding window rate limiter backed by SQLite.
        Returns True if within limit, False if limit exceeded.
        """
        now = time.time()
        db = get_db()
        conn = db.get_connection()
        with conn:
            cur = conn.execute("SELECT count, window_start FROM rate_limits WHERE key = ?", (key,))
            row = cur.fetchone()

            if not row:
                conn.execute(
                    "INSERT INTO rate_limits (key, count, window_start) VALUES (?, 1, ?)",
                    (key, now)
                )
                return True

            count, window_start = row["count"], row["window_start"]
            if now - window_start > window_seconds:
                conn.execute(
                    "UPDATE rate_limits SET count = 1, window_start = ? WHERE key = ?",
                    (now, key)
                )
                return True
            elif count >= max_requests:
                return False
            else:
                conn.execute(
                    "UPDATE rate_limits SET count = count + 1 WHERE key = ?",
                    (key,)
                )
                return True

    def check_guest_rate_limit(self, client_ip: str, increment: bool = False) -> Tuple[bool, int]:
        """
        Check and enforce guest analysis rate limit: max 10 requests per 10 minutes per IP.
        In local development (APP_ENV != 'production' and dev_unlimited_guest_quota=True),
        local loopback addresses (127.0.0.1, ::1, localhost, testclient) are granted unlimited quota
        to allow repeatable testing of real uploaded notices without registration friction.
        Production environment strictly enforces guest_rate_limit_per_window (10/10min) for all IPs.
        Returns: (is_allowed, remaining_quota)
        """
        is_loopback = _is_dev_client_ip(client_ip)
        is_dev_unlimited = getattr(config, "dev_unlimited_guest_quota", True) and getattr(config, "app_env", "development").lower() != "production"
        if is_loopback and is_dev_unlimited:
            return True, 999

        max_reqs = int(getattr(config, "guest_rate_limit_per_window", 10))
        window_sec = 600.0  # 10 minutes
        key = f"guest_limit:{client_ip}"
        now = time.time()
        db = get_db()
        conn = db.get_connection()
        with conn:
            cur = conn.execute("SELECT count, window_start FROM rate_limits WHERE key = ?", (key,))
            row = cur.fetchone()
            if not row:
                if increment:
                    conn.execute("INSERT INTO rate_limits (key, count, window_start) VALUES (?, 1, ?)", (key, now))
                    return True, max(0, max_reqs - 1)
                return True, max_reqs


            count, window_start = row["count"], row["window_start"]
            if now - window_start > window_sec:
                if increment:
                    conn.execute("UPDATE rate_limits SET count = 1, window_start = ? WHERE key = ?", (now, key))
                    return True, max(0, max_reqs - 1)
                return True, max_reqs

            elif count >= max_reqs:
                return False, 0
            else:
                if increment:
                    conn.execute("UPDATE rate_limits SET count = count + 1 WHERE key = ?", (key,))
                    return True, max(0, max_reqs - (count + 1))
                return True, max(0, max_reqs - count)

    def consume_guest_quota(self, client_ip: str) -> Tuple[bool, int]:
        """
        Atomically consumes one unit of guest quota when a valid analysis request begins.
        Returns: (is_allowed, remaining_quota)
        """
        return self.check_guest_rate_limit(client_ip, increment=True)

    def refund_guest_quota(self, client_ip: str) -> None:
        """
        Refunds one quota unit if analysis fails due to backend/infrastructure downtime.
        Prevents guest penalty on local Ollama offline or missing model errors.
        """
        is_loopback = _is_dev_client_ip(client_ip)
        is_dev_unlimited = getattr(config, "dev_unlimited_guest_quota", True) and getattr(config, "app_env", "development").lower() != "production"
        if is_loopback and is_dev_unlimited:
            return

        key = f"guest_limit:{client_ip}"
        db = get_db()
        conn = db.get_connection()
        with conn:
            conn.execute("UPDATE rate_limits SET count = MAX(0, count - 1) WHERE key = ?", (key,))

    def check_ocr_rate_limit(self, client_ip: str, is_authenticated: bool = False) -> Tuple[bool, int]:
        """
        Enforces rate limiting on OCR requests (default 30/min for guests, 60/min for authenticated citizens).
        Loopback IPs in local development are exempt to facilitate testing.
        Returns: (is_allowed, remaining_quota)
        """
        is_dev_client = _is_dev_client_ip(client_ip)
        is_dev_unlimited = getattr(config, "dev_unlimited_guest_quota", True) and getattr(config, "app_env", "development").lower() != "production"
        if is_dev_client and is_dev_unlimited:
            return True, 999

        max_reqs = getattr(config, "ocr_rate_limit_auth_per_min", 60) if is_authenticated else getattr(config, "ocr_rate_limit_guest_per_min", 30)
        window_sec = 60.0
        key = f"ocr_limit:{'auth' if is_authenticated else 'guest'}:{client_ip}"
        now = time.time()
        db = get_db()
        conn = db.get_connection()
        with conn:
            cur = conn.execute("SELECT count, window_start FROM rate_limits WHERE key = ?", (key,))
            row = cur.fetchone()
            if not row:
                conn.execute("INSERT INTO rate_limits (key, count, window_start) VALUES (?, 1, ?)", (key, now))
                return True, max(0, max_reqs - 1)

            count, window_start = row["count"], row["window_start"]
            if now - window_start > window_sec:
                conn.execute("UPDATE rate_limits SET count = 1, window_start = ? WHERE key = ?", (now, key))
                return True, max(0, max_reqs - 1)
            elif count >= max_reqs:
                return False, 0
            else:
                conn.execute("UPDATE rate_limits SET count = count + 1 WHERE key = ?", (key,))
                return True, max(0, max_reqs - (count + 1))


    # --------------------------------------------------------------------------
    # Registration & Direct Persistence (No OTP Required)
    # --------------------------------------------------------------------------
    async def register_user(self, name: str, email: str, password: str, client_ip: str = "unknown") -> Dict[str, Any]:
        """Register a new citizen account with immediate persistent database storage and session creation (no OTP)."""
        normalized_email = email.strip().lower()
        user_name = name.strip()

        # Enforce rate limit on registrations: max 10 per 10 minutes per IP
        is_dev = _is_dev_client_ip(client_ip) and getattr(config, "app_env", "development").lower() != "production"
        if not is_dev and not self.check_rate_limit(f"reg_ip:{client_ip}", 10, 600):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many registration attempts. Please wait a few minutes before trying again."
            )

        # Check username requirements
        if len(user_name) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 2 characters long."
            )
        if len(user_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username cannot exceed 100 characters."
            )

        # Check password strength
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long."
            )
        if len(password) > 128:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot exceed 128 characters."
            )

        db = get_db()
        conn = db.get_connection()
        with conn:
            cur = conn.execute("SELECT id, name, is_verified FROM users WHERE email = ?", (normalized_email,))
            existing = cur.fetchone()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already registered. Please sign in."
                )

            # Create new user directly active & verified (is_verified = 1)
            user_id = str(uuid.uuid4())
            pwd_hash = hash_password(password)
            now = self._now_iso()

            conn.execute(
                """
                INSERT INTO users (id, email, name, password_hash, is_verified, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
                """,
                (user_id, normalized_email, user_name, pwd_hash, now, now)
            )

            # Create immediate active session for auto-login
            expire_hours = int(getattr(config, "auth_session_expire_hours", 168))
            session_token = generate_secure_token(32)
            token_hash = hash_token(session_token)
            expires_at = self._expires_iso(hours=expire_hours)
            session_id = str(uuid.uuid4())

            conn.execute(
                """
                INSERT INTO sessions (id, user_id, session_token_hash, user_agent, ip_address, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, user_id, token_hash, "Registration", client_ip, expires_at, now)
            )

        user_public = {
            "id": user_id,
            "email": normalized_email,
            "name": user_name,
            "username": user_name,
            "is_verified": True,
            "created_at": now,
            "is_guest": False
        }

        return {
            "status": "success",
            "message": "Account created successfully.",
            "user": user_public,
            "session_token": session_token
        }

    async def verify_email(self, token: Optional[str] = None, email: Optional[str] = None, code: Optional[str] = None) -> Dict[str, Any]:
        """Verify an account using either the URL link token or email + 6-digit code."""
        if not token and not (email and code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either a verification token or an email with a 6-digit code is required."
            )

        db = get_db()
        conn = db.get_connection()
        with conn:
            if token:
                t_hash = hash_token(token)
                cur = conn.execute(
                    """
                    SELECT id, user_id, attempts, max_attempts, expires_at, used_at
                    FROM auth_tokens
                    WHERE token_type = 'verify_email' AND token_hash = ?
                    """,
                    (t_hash,)
                )
                token_row = cur.fetchone()

                if not token_row:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid or expired verification link."
                    )
                if token_row["used_at"] is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="This verification link has already been used. Please log in."
                    )
                if self._is_expired(token_row["expires_at"]):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="This verification link has expired. Please request a new verification email."
                    )

                user_id = token_row["user_id"]
                token_id = token_row["id"]
            else:
                norm_email = email.strip().lower()
                cur = conn.execute("SELECT id, is_verified FROM users WHERE email = ?", (norm_email,))
                user = cur.fetchone()

                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid email address or verification code."
                    )
                if user["is_verified"]:
                    return {
                        "status": "success",
                        "message": "Email is already verified. You may sign in."
                    }

                user_id = user["id"]

                cur = conn.execute(
                    """
                    SELECT id, attempts, max_attempts, expires_at, used_at, token_hash
                    FROM auth_tokens
                    WHERE user_id = ? AND token_type = 'verify_email_code' AND used_at IS NULL
                    ORDER BY created_at DESC LIMIT 1
                    """,
                    (user_id,)
                )
                code_row = cur.fetchone()

                if not code_row:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No active verification request found. Please request a new verification email."
                    )

                if code_row["attempts"] >= code_row["max_attempts"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Too many failed verification attempts. Please request a new verification code."
                    )

                if self._is_expired(code_row["expires_at"]):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Verification code has expired. Please request a new code."
                    )

                if not verify_code(code, code_row["token_hash"]):
                    conn.execute(
                        "UPDATE auth_tokens SET attempts = attempts + 1 WHERE id = ?",
                        (code_row["id"],)
                    )
                    conn.commit()
                    if code_row["attempts"] + 1 >= code_row["max_attempts"]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Too many failed verification attempts. Please request a new verification code."
                        )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid verification code. Please check the 6 digits and try again."
                    )

                token_id = code_row["id"]

            now = self._now_iso()
            conn.execute("UPDATE users SET is_verified = 1, updated_at = ? WHERE id = ?", (now, user_id))
            conn.execute(
                "UPDATE auth_tokens SET used_at = ? WHERE user_id = ? AND token_type LIKE 'verify_email%' AND used_at IS NULL",
                (now, user_id)
            )

        return {
            "status": "success",
            "message": "Email verified successfully! You may now sign in to SuchnaSetu AI."
        }

    async def resend_verification(self, email: str, client_ip: str = "unknown") -> Dict[str, Any]:
        """Resend verification email with cooldown throttling."""
        norm_email = email.strip().lower()

        if not self.check_rate_limit(f"resend:{norm_email}", 1, 60):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please wait at least 60 seconds before requesting another verification email."
            )

        if not self.check_rate_limit(f"resend_hourly:{norm_email}", 5, 3600):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many resend attempts for this email address. Please try again later."
            )

        db = get_db()
        conn = db.get_connection()
        with conn:
            cur = conn.execute("SELECT id, name, is_verified FROM users WHERE email = ?", (norm_email,))
            user = cur.fetchone()

            if user:
                if user["is_verified"]:
                    return {
                        "status": "success",
                        "message": "This account is already verified and active. You can sign in directly with your password.",
                        "email_delivered": False,
                        "already_verified": True
                    }

                now = self._now_iso()
                token_expiry = self._expires_iso(hours=getattr(config, "auth_verify_expire_hours", 24))
                verify_token = generate_secure_token(32)
                verify_code = generate_secure_code(6)

                delivery = await email_service.send_verification_email(
                    email=norm_email,
                    name=user["name"],
                    token=verify_token,
                    code=verify_code
                )

                if not delivery.success:
                    return {
                        "status": "warning",
                        "message": "Unable to deliver verification email due to mail server connectivity. Your existing code remains valid.",
                        "email_delivered": False
                    }

                conn.execute(
                    "UPDATE auth_tokens SET used_at = ? WHERE user_id = ? AND token_type LIKE 'verify_email%' AND used_at IS NULL",
                    (now, user["id"])
                )
                conn.execute(
                    """
                    INSERT INTO auth_tokens (id, user_id, token_type, token_hash, max_attempts, expires_at, created_at)
                    VALUES (?, ?, 'verify_email', ?, 5, ?, ?)
                    """,
                    (str(uuid.uuid4()), user["id"], hash_token(verify_token), token_expiry, now)
                )
                conn.execute(
                    """
                    INSERT INTO auth_tokens (id, user_id, token_type, token_hash, max_attempts, expires_at, created_at)
                    VALUES (?, ?, 'verify_email_code', ?, 5, ?, ?)
                    """,
                    (str(uuid.uuid4()), user["id"], hash_code(verify_code), token_expiry, now)
                )

        return {
            "status": "success",
            "message": "A new verification email with code and link has been dispatched.",
            "email_delivered": True
        }

    # --------------------------------------------------------------------------
    # Login, Session & Account Inspection
    # --------------------------------------------------------------------------
    async def login_user(
        self,
        email: str,
        password: str,
        remember_me: bool = False,
        user_agent: Optional[str] = None,
        client_ip: str = "unknown"
    ) -> Tuple[str, Dict[str, Any]]:
        """Authenticate user with Argon2id and create a secure server-managed session."""
        norm_email = email.strip().lower()
        rate_key = f"login_fail:{client_ip}_{norm_email}"

        db = get_db()
        conn = db.get_connection()
        with conn:
            cur = conn.execute(
                "SELECT id, email, name, password_hash, is_verified, created_at FROM users WHERE email = ?",
                (norm_email,)
            )
            user = cur.fetchone()

        if not user or not verify_password(password, user["password_hash"]):
            self.check_rate_limit(rate_key, 5, 300)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Ensure account is active and marked verified
        if not user["is_verified"]:
            with conn:
                conn.execute("UPDATE users SET is_verified = 1 WHERE id = ?", (user["id"],))

        expire_hours = 720 if remember_me else getattr(config, "auth_session_expire_hours", 168)
        session_token = generate_secure_token(32)
        token_hash = hash_token(session_token)
        now = self._now_iso()
        expires_at = self._expires_iso(hours=expire_hours)
        session_id = str(uuid.uuid4())

        with conn:
            conn.execute(
                """
                INSERT INTO sessions (id, user_id, session_token_hash, user_agent, ip_address, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, user["id"], token_hash, user_agent, client_ip, expires_at, now)
            )

        user_public = {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "is_verified": bool(user["is_verified"]),
            "created_at": user["created_at"],
            "is_guest": False
        }

        return session_token, user_public

    def get_user_by_session_token(self, raw_session_token: str) -> Optional[Dict[str, Any]]:
        """Resolve an authenticated citizen from an opaque session token."""
        if not raw_session_token or len(raw_session_token.strip()) < 16:
            return None

        token_hash = hash_token(raw_session_token)
        db = get_db()
        conn = db.get_connection()
        with conn:
            cur = conn.execute(
                """
                SELECT s.id as session_id, s.expires_at, u.id, u.email, u.name, u.is_verified, u.created_at
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token_hash = ?
                """,
                (token_hash,)
            )
            row = cur.fetchone()

            if not row:
                return None

            if self._is_expired(row["expires_at"]):
                conn.execute("DELETE FROM sessions WHERE id = ?", (row["session_id"],))
                return None

            return {
                "id": row["id"],
                "email": row["email"],
                "name": row["name"],
                "is_verified": bool(row["is_verified"]),
                "created_at": row["created_at"],
                "session_id": row["session_id"],
                "is_guest": False
            }

    def logout_session(self, raw_session_token: str) -> bool:
        """Invalidate a server session."""
        if not raw_session_token:
            return False

        token_hash = hash_token(raw_session_token)
        db = get_db()
        conn = db.get_connection()
        with conn:
            conn.execute("DELETE FROM sessions WHERE session_token_hash = ?", (token_hash,))
        return True

    # --------------------------------------------------------------------------
    # Password Recovery Flow
    # --------------------------------------------------------------------------
    async def request_password_reset(self, email: str, method: str = "code", client_ip: str = "unknown") -> Dict[str, Any]:
        """Send a password recovery 6-digit code or magic link."""
        norm_email = email.strip().lower()

        is_dev = _is_dev_client_ip(client_ip) and getattr(config, "app_env", "development").lower() != "production"
        if not is_dev and not self.check_rate_limit(f"pw_reset_ip:{client_ip}", 5, 900):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many password reset requests. Please wait before trying again."
            )

        db = get_db()
        conn = db.get_connection()
        with conn:
            cur = conn.execute("SELECT id, name, is_verified FROM users WHERE email = ?", (norm_email,))
            user = cur.fetchone()

            if not user:
                return {
                    "status": "success",
                    "message": "If an account exists with this email address, password recovery instructions have been sent."
                }

            now = self._now_iso()
            token_expiry = self._expires_iso(minutes=getattr(config, "auth_token_expire_minutes", 15))

            conn.execute(
                "UPDATE auth_tokens SET used_at = ? WHERE user_id = ? AND token_type LIKE 'reset_password%' AND used_at IS NULL",
                (now, user["id"])
            )

            if method == "link":
                reset_token = generate_secure_token(32)
                conn.execute(
                    """
                    INSERT INTO auth_tokens (id, user_id, token_type, token_hash, max_attempts, expires_at, created_at)
                    VALUES (?, ?, 'reset_password', ?, 5, ?, ?)
                    """,
                    (str(uuid.uuid4()), user["id"], hash_token(reset_token), token_expiry, now)
                )
                await email_service.send_password_reset_link(
                    email=norm_email,
                    name=user["name"],
                    token=reset_token
                )
            else:
                reset_code = generate_secure_code(6)
                conn.execute(
                    """
                    INSERT INTO auth_tokens (id, user_id, token_type, token_hash, max_attempts, expires_at, created_at)
                    VALUES (?, ?, 'reset_password_code', ?, 5, ?, ?)
                    """,
                    (str(uuid.uuid4()), user["id"], hash_code(reset_code), token_expiry, now)
                )
                await email_service.send_password_reset_code(
                    email=norm_email,
                    name=user["name"],
                    code=reset_code
                )

        return {
            "status": "success",
            "message": "If an account exists with this email address, password recovery instructions have been sent."
        }

    async def reset_password(
        self,
        new_password: str,
        token: Optional[str] = None,
        email: Optional[str] = None,
        code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify recovery credential, set a new Argon2id password, and revoke previous sessions."""
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long."
            )

        if not token and not (email and code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either a reset token or an email with a 6-digit recovery code is required."
            )

        db = get_db()
        conn = db.get_connection()
        with conn:
            if token:
                t_hash = hash_token(token)
                cur = conn.execute(
                    """
                    SELECT id, user_id, expires_at, used_at
                    FROM auth_tokens
                    WHERE token_type = 'reset_password' AND token_hash = ?
                    """,
                    (t_hash,)
                )
                token_row = cur.fetchone()

                if not token_row:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid or expired password reset link."
                    )
                if token_row["used_at"] is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="This password reset link has already been used."
                    )
                if self._is_expired(token_row["expires_at"]):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="This password reset link has expired. Please request a new one."
                    )

                user_id = token_row["user_id"]
            else:
                norm_email = email.strip().lower()
                cur = conn.execute("SELECT id, name FROM users WHERE email = ?", (norm_email,))
                user = cur.fetchone()

                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid email address or recovery code."
                    )

                user_id = user["id"]

                cur = conn.execute(
                    """
                    SELECT id, attempts, max_attempts, expires_at, used_at, token_hash
                    FROM auth_tokens
                    WHERE user_id = ? AND token_type = 'reset_password_code' AND used_at IS NULL
                    ORDER BY created_at DESC LIMIT 1
                    """,
                    (user_id,)
                )
                code_row = cur.fetchone()

                if not code_row:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No active password recovery request found. Please request a new code."
                    )

                if code_row["attempts"] >= code_row["max_attempts"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Too many failed recovery attempts. This code is invalidated. Please request a new code."
                    )

                if self._is_expired(code_row["expires_at"]):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Recovery code has expired. Please request a new code."
                    )

                if not verify_code(code, code_row["token_hash"]):
                    conn.execute(
                        "UPDATE auth_tokens SET attempts = attempts + 1 WHERE id = ?",
                        (code_row["id"],)
                    )
                    conn.commit()
                    if code_row["attempts"] + 1 >= code_row["max_attempts"]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Too many failed recovery attempts. This code is invalidated. Please request a new code."
                        )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid recovery code. Please check the code and try again."
                    )

            now = self._now_iso()
            pwd_hash = hash_password(new_password)

            conn.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?", (pwd_hash, now, user_id))
            conn.execute(
                "UPDATE auth_tokens SET used_at = ? WHERE user_id = ? AND token_type LIKE 'reset_password%' AND used_at IS NULL",
                (now, user_id)
            )

            # Revoke all active sessions for this user
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))

            cur = conn.execute("SELECT email, name FROM users WHERE id = ?", (user_id,))
            updated_user = cur.fetchone()

        if updated_user:
            await email_service.send_password_changed_notification(
                email=updated_user["email"],
                name=updated_user["name"]
            )

        return {
            "status": "success",
            "message": "Password updated successfully. All existing sessions have been signed out. You can now log in with your new password."
        }


auth_service = AuthService()
