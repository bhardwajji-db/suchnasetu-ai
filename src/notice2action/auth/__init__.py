"""
SuchnaSetu AI Authentication and Account Management Package.
"""

from notice2action.auth.security import hash_password, verify_password, hash_token, hash_code, verify_code
from notice2action.auth.email_service import email_service
from notice2action.auth.auth_service import auth_service
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

__all__ = [
    "hash_password",
    "verify_password",
    "hash_token",
    "hash_code",
    "verify_code",
    "email_service",
    "auth_service",
    "RegisterRequest",
    "VerifyEmailRequest",
    "ResendVerificationRequest",
    "LoginRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "UserPublic",
    "AuthResponse",
    "GuestStatusResponse",
]
