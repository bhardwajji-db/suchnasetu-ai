"""
Pydantic Schemas for Authentication and User Account Requests/Responses.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Citizen full name")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Secure password")
    confirm_password: Optional[str] = Field(None, description="Password confirmation")


class VerifyEmailRequest(BaseModel):
    token: Optional[str] = Field(None, description="Opaque URL verification token")
    email: Optional[EmailStr] = Field(None, description="Citizen email address")
    code: Optional[str] = Field(None, min_length=6, max_length=6, description="6-digit verification code")


class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Citizen email address")
    password: str = Field(..., description="Citizen password")
    remember_me: bool = Field(False, description="Extend session lifetime to 30 days")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    method: str = Field("code", description="Recovery method: 'code' (6-digit OTP) or 'link' (URL)")


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    confirm_password: Optional[str] = Field(None, description="Confirm new password")
    token: Optional[str] = Field(None, description="Password reset token from magic link")
    email: Optional[EmailStr] = Field(None, description="Citizen email address (required with code)")
    code: Optional[str] = Field(None, min_length=6, max_length=6, description="6-digit one-time recovery code")


class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    is_verified: bool
    created_at: str
    is_guest: bool = False


class AuthResponse(BaseModel):
    status: str
    message: str
    user: Optional[UserPublic] = None
    email_delivered: Optional[bool] = None
    already_verified: Optional[bool] = None


class GuestStatusResponse(BaseModel):
    is_guest: bool
    ip: str
    remaining_analyses: int
    limit_window_minutes: int
