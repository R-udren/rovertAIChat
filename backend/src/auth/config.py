import os
from datetime import timedelta
from typing import Optional

from fastapi import Request, Response
from src.core.logger import app_logger

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysupersecretkey")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "myrefreshsecretkey")
COOKIE_DOMAIN = os.getenv("DOMAIN", "localhost")
COOKIE_SECURE = os.getenv("ENVIRONMENT", "production") == "production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


# Function to determine if we should use secure cookies and domain
def get_cookie_config(request: Optional[Request] = None):
    """
    Determine cookie configuration based on the request host.
    Returns (secure, domain) tuple.
    """
    if request and hasattr(request, "headers"):
        host = request.headers.get("host", "").lower()

        # If it's localhost or local IP, don't use secure cookies and no domain restriction
        if (
            "localhost" in host
            or "127.0.0.1" in host
            or "0.0.0.0" in host
            or host.startswith("192.168.")
            or host.startswith("10.")
        ):
            return False, None
        else:
            # For real domains, use secure cookies and set domain
            return True, COOKIE_DOMAIN if COOKIE_DOMAIN != "localhost" else None

    # Fallback to environment-based configuration
    return COOKIE_SECURE, COOKIE_DOMAIN if COOKIE_DOMAIN != "localhost" else None


# Convert durations to timedelta objects for easier use
ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_DELTA = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

# Log configuration details
app_logger.debug(f"JWT algorithm: {ALGORITHM}")
app_logger.debug(
    f"JWT secret key: {'*' * (len(SECRET_KEY) // 2) + SECRET_KEY[len(SECRET_KEY) // 2 :]}"
)
app_logger.debug(
    f"JWT refresh secret key: {'*' * (len(REFRESH_SECRET_KEY) // 2) + REFRESH_SECRET_KEY[len(REFRESH_SECRET_KEY) // 2 :]}"
)
app_logger.debug(f"Access token expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
app_logger.debug(f"Refresh token expiry: {REFRESH_TOKEN_EXPIRE_DAYS} days")
app_logger.debug(f"Cookie domain: {COOKIE_DOMAIN}")
app_logger.debug(f"Cookie secure: {COOKIE_SECURE}")


# Set cookies helper function
def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    request: Optional[Request] = None,
):
    secure, domain = get_cookie_config(request)

    cookie_kwargs = {
        "httponly": True,
        "secure": secure,
        "samesite": "lax",
    }

    if domain:
        cookie_kwargs["domain"] = domain

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/api",
        **cookie_kwargs,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth/refresh",
        **cookie_kwargs,
    )


# Clear cookies helper function
def clear_auth_cookies(response: Response, request: Optional[Request] = None):
    secure, domain = get_cookie_config(request)

    cookie_kwargs = {}
    if domain:
        cookie_kwargs["domain"] = domain

    response.delete_cookie(key="access_token", path="/", **cookie_kwargs)

    response.delete_cookie(
        key="refresh_token", path="/api/v1/auth/refresh", **cookie_kwargs
    )
