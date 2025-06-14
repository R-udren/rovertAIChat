from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from src.auth.jwt import decode_token, verify_password
from src.core.logger import app_logger
from src.database import get_db
from src.models.user import User
from src.schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    if not username:
        app_logger.error("Empty username provided")
        return None

    try:
        app_logger.debug(f"Looking up user by username: {username}")
        return db.query(User).filter(User.username == username).first()
    except Exception as e:
        app_logger.error(f"Error getting user by username: {str(e)}")
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    if not email:
        app_logger.error("Empty email provided")
        return None

    try:
        app_logger.debug(f"Looking up user by email: {email}")
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        app_logger.error(f"Error getting user by email: {str(e)}")
        return None


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    if not user_id:
        app_logger.error("Empty user_id provided")
        return None

    try:
        # Convert string to UUID
        uuid_id = UUID(user_id)
        return db.query(User).filter(User.id == uuid_id).first()
    except Exception as e:
        app_logger.error(f"Error getting user by ID: {str(e)}")
        return None


def authenticate_user(
    db: Session, email_or_username: str, password: str
) -> Optional[User]:
    """Authenticate a user with email or username and password."""
    app_logger.info(f"Attempting authentication for: {email_or_username}")

    # First try to find user by username
    user = get_user_by_username(db, email_or_username)

    # If not found by username, try by email
    if not user:
        user = get_user_by_email(db, email_or_username)

    # Check if user exists
    if not user:
        app_logger.warning(
            f"Authentication failed: No user found with credential: {email_or_username}"
        )
        return None

    # Verify password
    if not verify_password(password, user.password_hash):
        app_logger.warning(
            f"Authentication failed: Invalid password for user: {user.username}"
        )
        return None

    app_logger.info(f"User authenticated successfully: {user.username}")
    return user


def update_last_login(db: Session, user: User) -> None:
    """Update the user's last login timestamp."""
    setattr(user, "last_login", datetime.now(timezone.utc))
    db.commit()
    app_logger.debug(f"Last login updated for user: {user.username}")


def increment_token_version(db: Session, user: User) -> None:
    """Increment the user's token version to invalidate existing tokens."""
    setattr(user, "token_version", user.token_version + 1)
    db.commit()
    app_logger.debug(f"Token version incremented for user: {user.username}")


def get_current_user(
    access_token: str = Cookie(None), db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    if access_token is None:
        app_logger.warning("No access token provided in cookies")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(access_token)
        user_id = payload.get("sub")
        token_version = payload.get("token_version")
        if user_id is None:
            app_logger.warning("Token missing 'sub' claim")
            raise credentials_exception
        token_data = TokenData(user_id=str(user_id))
    except JWTError as e:
        app_logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception

    user = get_user_by_id(db, token_data.user_id)
    if user is None:
        app_logger.warning(f"User from token not found: {token_data.user_id}")
        raise credentials_exception
    if user.is_active is False:
        app_logger.warning(f"Attempt to authenticate with inactive user: {user.id}")
        raise HTTPException(status_code=400, detail="Inactive user")
        # Validate token version - using string comparison to avoid type issues
    if token_version is None or str(token_version) != str(user.token_version):
        app_logger.warning(f"Token version mismatch for user: {user.id}")
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current user and verify they are active."""
    if current_user.is_active is False:
        app_logger.warning(f"Inactive user attempt: {current_user.id}")
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get the current user and verify they are an admin."""
    if current_user.is_admin() is False:
        app_logger.warning(f"Non-admin user attempt: {current_user.id}")
        raise HTTPException(status_code=403, detail="Not an admin user")
    return current_user
