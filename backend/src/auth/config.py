import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import Response
from src.core.logger import app_logger

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysupersecretkey")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "myrefreshsecretkey")
COOKIE_DOMAIN = os.getenv("DOMAIN", "localhost")
COOKIE_SECURE = False  # os.getenv("ENVIRONMENT", "development") == "production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Token blacklist for logout functionality
# This is a simple in-memory blacklist - for production, use Redis or a database
TOKEN_BLACKLIST = set()

# Convert durations to timedelta objects for easier use
ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_DELTA = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

# Log configuration details
app_logger.debug(f"JWT algorithm: {ALGORITHM}")
app_logger.debug(f"Access token expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
app_logger.debug(f"Refresh token expiry: {REFRESH_TOKEN_EXPIRE_DAYS} days")
app_logger.debug(f"Cookie domain: {COOKIE_DOMAIN}")
app_logger.debug(f"Cookie secure: {COOKIE_SECURE}")


# Set cookies helper function
def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=COOKIE_DOMAIN,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/auth/refresh",  # Restrict path for security
        domain=COOKIE_DOMAIN,
    )


# Clear cookies helper function
def clear_auth_cookies(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        domain=COOKIE_DOMAIN,
    )

    response.delete_cookie(
        key="refresh_token",
        path="/api/auth/refresh",
        domain=COOKIE_DOMAIN,
    )
