"""
Authentication Security Layer for SuchnaSetu AI.
Handles:
- Argon2id password hashing and constant-time verification
- HMAC-SHA256 digests for sensitive session tokens and 6-digit numeric recovery codes
- Cryptographically secure URL-safe token generation and 6-digit OTP code generation
"""

import hmac
import hashlib
import secrets
import logging
from typing import Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from notice2action.config import config

logger = logging.getLogger("notice2action.auth.security")

# Argon2id hasher with balanced secure parameters: 64 MiB memory cost, time_cost=2
_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    hash_len=32
)


def get_auth_secret_key() -> str:
    """Return configured auth secret key with safe fallback for dev."""
    return getattr(config, "auth_secret_key", None) or "suchnasetu-dev-insecure-secret-key-change-in-production"


def hash_password(plain_password: str) -> str:
    """Hash a password using Argon2id."""
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against an Argon2id hash."""
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False
    except Exception as e:
        logger.warning(f"Unexpected error during password verification: {e}")
        return False


def hash_token(raw_token: str, secret_key: Optional[str] = None) -> str:
    """
    Produce a server-secret-keyed HMAC-SHA256 hex digest of an opaque token.
    Tokens are stored in the database ONLY as HMAC digests to protect sessions and links.
    """
    key = (secret_key or get_auth_secret_key()).encode("utf-8")
    return hmac.new(key, raw_token.strip().encode("utf-8"), hashlib.sha256).hexdigest()


def hash_code(raw_code: str, secret_key: Optional[str] = None) -> str:
    """
    Produce a server-secret-keyed HMAC-SHA256 hex digest of a 6-digit numeric code.
    Prevents offline rainbow table and dictionary attacks on small numeric spaces (000000-999999).
    """
    key = (secret_key or get_auth_secret_key()).encode("utf-8")
    return hmac.new(key, raw_code.strip().encode("utf-8"), hashlib.sha256).hexdigest()


def verify_code(raw_code: str, stored_hash: str, secret_key: Optional[str] = None) -> bool:
    """Verify a 6-digit code against its stored HMAC digest using constant-time comparison."""
    expected_hash = hash_code(raw_code, secret_key)
    return hmac.compare_digest(expected_hash, stored_hash)


def verify_token_hash(raw_token: str, stored_hash: str, secret_key: Optional[str] = None) -> bool:
    """Verify an opaque token against its stored HMAC digest using constant-time comparison."""
    expected_hash = hash_token(raw_token, secret_key)
    return hmac.compare_digest(expected_hash, stored_hash)


def generate_secure_token(nbytes: int = 32) -> str:
    """Generate a high-entropy URL-safe cryptographic token."""
    return secrets.token_urlsafe(nbytes)


def generate_secure_code(digits: int = 6) -> str:
    """Generate a cryptographically secure numeric code (e.g. 6-digit recovery code)."""
    min_val = 10 ** (digits - 1)
    max_val = (10 ** digits) - 1
    code = secrets.randbelow(max_val - min_val + 1) + min_val
    return str(code)
