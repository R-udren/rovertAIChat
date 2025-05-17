from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
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
    app_logger.debug(f"Looking up user by username: {username}")
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    app_logger.debug(f"Looking up user by email: {email}")
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    app_logger.debug(f"Looking up user by ID: {user_id}")
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password."""
    app_logger.info(f"Authenticating user: {username}")
    user = get_user_by_username(db, username)
    if not user:
        app_logger.warning(f"Authentication failed: User not found - {username}")
        return None
    if not verify_password(password, user.password_hash):
        app_logger.warning(
            f"Authentication failed: Invalid password for user - {username}"
        )
        return None
    app_logger.info(f"User authenticated successfully: {username}")
    return user


def update_last_login(db: Session, user: User) -> None:
    """Update the user's last login timestamp."""
    app_logger.debug(f"Updating last login for user: {user.username}")
    setattr(user, "last_login", datetime.now(timezone.utc))
    db.commit()
    app_logger.debug(f"Last login updated for user: {user.username}")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    app_logger.debug("Authenticating request with JWT token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            app_logger.warning("Token missing 'sub' claim")
            raise credentials_exception
        token_data = TokenData(user_id=str(user_id))
        app_logger.debug(f"Token validated for user_id: {user_id}")
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

    app_logger.debug(f"User authenticated via token: {user.username}")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current user and verify they are active."""
    if current_user.is_active is False:
        app_logger.warning(f"Inactive user attempt: {current_user.id}")
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
