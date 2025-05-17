from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import jwt

from src.auth.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)


def verify_password(plain_password, hashed_password):
    """Verify a password against a hash."""
    # Convert strings to bytes if needed
    if isinstance(plain_password, str):
        plain_password = plain_password.encode("utf-8")
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")

    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """Generate a password hash with salt."""
    # Convert string to bytes if needed
    if isinstance(password, str):
        password = password.encode("utf-8")

    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)

    return hashed.decode("utf-8")


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new JWT access token.

    Args:
        data: The data to encode in the token.
        expires_delta: Optional expiration time.

    Returns:
        Encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new JWT refresh token.

    Args:
        data: The data to encode in the token.
        expires_delta: Optional expiration time.

    Returns:
        Encoded JWT refresh token as a string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, is_refresh: bool = False) -> Dict[str, Any]:
    """
    Decode a JWT token.

    Args:
        token: The token to decode.
        is_refresh: Whether the token is a refresh token.

    Returns:
        The decoded token payload.
    """
    secret = REFRESH_SECRET_KEY if is_refresh else SECRET_KEY
    return jwt.decode(token, secret, algorithms=[ALGORITHM])
