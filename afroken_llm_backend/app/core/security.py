"""
Security utilities for authentication and JWT handling.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.config import settings


# Password hashing context (e.g. for future password-based auth).
# - Uses bcrypt as the hashing scheme.
# - `deprecated="auto"` lets Passlib transparently upgrade hashes if needed.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    - `subject` usually encodes the user identifier (e.g. phone number or user id).
    - `expires_delta` optionally overrides the default expiry window.
    """

    # Capture the current UTC time to anchor the expiry.
    now = datetime.utcnow()
    if expires_delta:
        # If a custom lifetime is provided, add it to `now`.
        exp = now + expires_delta
    else:
        # Otherwise, add the default number of minutes from settings.
        exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MIN)

    # JWT payload containing the subject and expiration timestamp.
    # Note: storing `exp` as an ISO string; some JWT tools expect a Unix timestamp.
    to_encode = {"sub": subject, "exp": exp.isoformat()}

    # Sign and encode the token using the configured secret and algorithm.
    encoded = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    # Return the compact serialized JWT string.
    return encoded


def verify_token(token: str):
    """
    Decode and verify a JWT.

    Returns the decoded payload dictionary if valid; otherwise returns None.
    """

    try:
        # Attempt to decode the token using the same secret and algorithm.
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except Exception:
        # On any error (expired, invalid signature, malformed), treat as invalid.
        return None

