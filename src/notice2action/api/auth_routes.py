"""
Authentication and Citizen Account Endpoints for SuchnaSetu AI.
Handles:
- User registration and account verification via 6-digit code or link
- Argon2id login with HttpOnly session cookies
- Session resolution and profile inspection (/api/auth/me)
- Expiring password recovery flows
- Genuinely restricted guest mode enforcement
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Response, HTTPException, status, Depends

from notice2action.config import config
from notice2action.auth.schemas import (
    RegisterRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserPublic,
    AuthResponse,
    GuestStatusResponse,
)
from notice2action.auth.auth_service import auth_service

logger = logging.getLogger("notice2action.api.auth")

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _extract_session_token(request: Request) -> Optional[str]:
    """Extract session token from cookie, Authorization header, or X-Session-Token."""
    cookie_name = getattr(config, "auth_cookie_name", "suchnasetu_session")
    cookie_token = request.cookies.get(cookie_name)
    if cookie_token:
        return cookie_token

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    x_session = request.headers.get("X-Session-Token")
    if x_session:
        return x_session.strip()

    return None


def get_client_ip(request: Request) -> str:
    """Safely resolve client IP address, only trusting reverse proxy headers from verified local proxies."""
    client_host = request.client.host if request.client else "127.0.0.1"
    trusted_proxies = set(getattr(config, "trusted_proxies", ["127.0.0.1", "::1", "localhost", "testclient"]))

    if client_host in trusted_proxies:
        cf_ip = request.headers.get("CF-Connecting-IP") or request.headers.get("cf-connecting-ip")
        if cf_ip and cf_ip.strip():
            return cf_ip.strip()
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for and forwarded_for.strip():
            return forwarded_for.split(",")[0].strip()

    return client_host


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency enforcing that the request is strictly authenticated.
    Raises HTTP 401 if unauthenticated or session expired.
    """
    token = _extract_session_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in to access this workspace."
        )

    user = auth_service.get_user_by_session_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please sign in again."
        )

    return user


async def get_optional_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Dependency that returns the authenticated user if present, or None if guest."""
    token = _extract_session_token(request)
    if not token:
        return None
    return auth_service.get_user_by_session_token(token)


async def get_current_user_or_guest(request: Request) -> Dict[str, Any]:
    """
    Dependency supporting authenticated citizens OR restricted guest access.
    - If valid session token present: returns authenticated citizen user.
    - If unauthenticated guest: enforces guest rate limits.
      Raises HTTP 429 if guest quota is exhausted; otherwise returns guest user context.
    """
    token = _extract_session_token(request)
    if token:
        user = auth_service.get_user_by_session_token(token)
        if user:
            return user

    # Guest user: attach identity context and remaining quota metadata.
    # Note: notice analysis rate limit is enforced specifically at analysis time (/api/analyze)
    # so that OCR extraction, preview, and read endpoints are never blocked by analysis quota.
    client_ip = get_client_ip(request)
    allowed, remaining = auth_service.check_guest_rate_limit(client_ip, increment=False)

    return {
        "id": f"guest_{hash(client_ip) % 1000000}",
        "email": None,
        "name": "Guest Citizen",
        "is_verified": False,
        "created_at": "",
        "is_guest": True,
        "client_ip": client_ip,
        "guest_remaining": remaining
    }


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, request: Request, response: Response):
    """Register a new citizen account without OTP and create an authenticated session."""
    client_ip = get_client_ip(request)
    if payload.confirm_password and payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match. Please re-enter your password."
        )

    user_name = payload.username or payload.name or ""
    res = await auth_service.register_user(
        name=user_name,
        email=str(payload.email),
        password=payload.password,
        client_ip=client_ip
    )

    session_token = res.get("session_token")
    if session_token:
        expire_hours = int(getattr(config, "auth_session_expire_hours", 168))
        max_age_seconds = expire_hours * 3600
        cookie_name = getattr(config, "auth_cookie_name", "suchnasetu_session")
        cookie_secure = _is_request_https(request)
        cookie_samesite = getattr(config, "auth_cookie_samesite", "lax")

        response.set_cookie(
            key=cookie_name,
            value=session_token,
            max_age=max_age_seconds,
            httponly=True,
            secure=cookie_secure,
            samesite=cookie_samesite,
            path="/"
        )

    user_obj = UserPublic(**res["user"]) if res.get("user") else None

    return AuthResponse(
        status=res["status"],
        message=res["message"],
        user=user_obj,
        email_delivered=False,
        already_verified=False
    )


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(payload: VerifyEmailRequest):
    """Verify an email address using either an email link token or a 6-digit code."""
    res = await auth_service.verify_email(
        token=payload.token,
        email=str(payload.email) if payload.email else None,
        code=payload.code
    )
    return AuthResponse(status=res["status"], message=res["message"])


@router.post("/resend-verification", response_model=AuthResponse)
async def resend_verification(payload: ResendVerificationRequest, request: Request):
    """Request a fresh verification link and code if account remains unverified."""
    client_ip = get_client_ip(request)
    res = await auth_service.resend_verification(str(payload.email), client_ip=client_ip)
    return AuthResponse(
        status=res["status"],
        message=res["message"],
        email_delivered=res.get("email_delivered"),
        already_verified=res.get("already_verified")
    )


def _is_request_https(request: Request) -> bool:
    """Determines if the request is served over HTTPS directly or via trusted reverse proxy."""
    if request.url.scheme == "https":
        return True

    # If auth_cookie_samesite is "none", modern browsers strictly require Secure=True.
    if getattr(config, "auth_cookie_samesite", "lax").lower() == "none":
        return True

    headers = getattr(request, "headers", {})
    proto = (headers.get("X-Forwarded-Proto") or headers.get("x-forwarded-proto")) if hasattr(headers, "get") else None
    if proto and str(proto).lower() == "https":
        return True

    client_host = request.client.host if request.client else "127.0.0.1"
    trusted_proxies = set(getattr(config, "trusted_proxies", ["127.0.0.1", "::1", "localhost", "testclient"]))

    if client_host in trusted_proxies:
        if proto and str(proto).lower() == "https":
            return True

    # If auth_cookie_secure is explicitly set to True, only enforce it if not on plain local HTTP test client
    # Direct local HTTP requests (e.g. http://127.0.0.1:8000) without X-Forwarded-Proto: https
    # should allow non-secure cookies so local browser testing does not drop session cookies.
    if getattr(config, "auth_cookie_secure", False):
        origin = ""
        if hasattr(request, "headers"):
            origin = request.headers.get("Origin") or request.headers.get("Referer") or ""
        if origin.startswith("http://127.0.0.1") or origin.startswith("http://localhost"):
            return False
        return True

    return False


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, request: Request, response: Response):
    """Authenticate with Argon2id and set an HttpOnly session cookie."""
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "Unknown")

    session_token, user_public = await auth_service.login_user(
        email=str(payload.email),
        password=payload.password,
        remember_me=payload.remember_me,
        user_agent=user_agent,
        client_ip=client_ip
    )

    expire_hours = 720 if payload.remember_me else int(getattr(config, "auth_session_expire_hours", 168))
    max_age_seconds = expire_hours * 3600
    cookie_name = getattr(config, "auth_cookie_name", "suchnasetu_session")
    cookie_secure = _is_request_https(request)
    cookie_samesite = getattr(config, "auth_cookie_samesite", "lax")

    response.set_cookie(
        key=cookie_name,
        value=session_token,
        max_age=max_age_seconds,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        path="/"
    )

    return AuthResponse(
        status="success",
        message="Sign in successful",
        user=UserPublic(**user_public)
    )


@router.post("/logout", response_model=AuthResponse)
async def logout(request: Request, response: Response):
    """Invalidate current server session and delete session cookie."""
    token = _extract_session_token(request)
    if token:
        auth_service.logout_session(token)

    cookie_name = getattr(config, "auth_cookie_name", "suchnasetu_session")
    cookie_secure = _is_request_https(request)
    cookie_samesite = getattr(config, "auth_cookie_samesite", "lax")

    response.delete_cookie(
        key=cookie_name,
        path="/",
        secure=cookie_secure,
        httponly=True,
        samesite=cookie_samesite
    )

    return AuthResponse(status="success", message="Successfully logged out.")


@router.get("/me", response_model=UserPublic)
async def get_current_account(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return the authenticated citizen's safe public profile."""
    return UserPublic(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        username=current_user.get("name"),
        is_verified=True,
        created_at=current_user["created_at"],
        is_guest=False
    )


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(payload: ForgotPasswordRequest, request: Request):
    """Send a password recovery 6-digit code or link."""
    client_ip = get_client_ip(request)
    res = await auth_service.request_password_reset(
        email=str(payload.email),
        method=payload.method,
        client_ip=client_ip
    )
    return AuthResponse(status=res["status"], message=res["message"])


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(payload: ResetPasswordRequest):
    """Verify recovery token or code, set a new Argon2id password, and revoke previous sessions."""
    if payload.confirm_password and payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match."
        )

    res = await auth_service.reset_password(
        new_password=payload.new_password,
        token=payload.token,
        email=str(payload.email) if payload.email else None,
        code=payload.code
    )
    return AuthResponse(status=res["status"], message=res["message"])


@router.get("/guest-status", response_model=GuestStatusResponse)
async def get_guest_status(request: Request):
    """Inspect remaining guest analysis quota."""
    client_ip = get_client_ip(request)
    allowed, remaining = auth_service.check_guest_rate_limit(client_ip, increment=False)
    return GuestStatusResponse(
        is_guest=True,
        ip=client_ip,
        remaining_analyses=remaining,
        limit_window_minutes=10
    )
