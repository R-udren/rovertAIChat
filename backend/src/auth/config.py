import os
from datetime import timedelta

from dotenv import load_dotenv

from src.core.logger import app_logger

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysupersecretkey")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "myrefreshsecretkey")
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
