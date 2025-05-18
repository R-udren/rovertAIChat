from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session
from src.auth.config import clear_auth_cookies, set_auth_cookies
from src.auth.jwt import create_access_token, create_refresh_token, decode_token
from src.auth.service import (
    authenticate_user,
    get_current_user,
    get_user_by_id,
    increment_token_version,
    update_last_login,
)
from src.core.logger import app_logger
from src.core.rate_limiter import limiter
from src.database import get_db
from src.models.user import User
from src.schemas.user import RefreshToken, Token, UserCreate, UserResponse
from src.services.user import create_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user.

    Returns:
        User object with the created user details
    """
    app_logger.info(f"Registering new user with username: {user.username}")
    db_user = create_user(db, user)
    app_logger.info(f"User registered successfully: {user.username}")
    return db_user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate and login a user.

    Returns:
        JWT access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    app_logger.info(f"Login attempt for user: {form_data.username}")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        app_logger.warning(f"Login failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_active is False:
        app_logger.warning(f"Login attempt for inactive user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    update_last_login(db, user)

    app_logger.debug(f"Creating JWT tokens for user: {user.username}")
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        token_version=user.token_version,
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, token_version=user.token_version
    )
    app_logger.info(f"User {user.username} logged in successfully")

    set_auth_cookies(
        response=response,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token_data: RefreshToken,
    db: Session = Depends(get_db),
):
    """
    Refresh an access token using a refresh token.

    Returns:
        New JWT access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    app_logger.debug("Token refresh requested")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(refresh_token_data.refresh_token, is_refresh=True)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        token_version = payload.get("token_version")

        if user_id is None or token_type != "refresh":
            app_logger.warning(
                "Invalid refresh token: missing sub claim or incorrect type"
            )
            raise credentials_exception

        # Get user from database
        user = get_user_by_id(db, user_id)

        if user is None or not user.get_active():
            app_logger.warning(
                f"Invalid refresh token: user not found or inactive - {user_id}"
            )
            raise credentials_exception

        # Validate token version
        if token_version is None or str(token_version) != str(user.token_version):
            app_logger.warning(f"Token version mismatch on refresh for user: {user.id}")
            raise credentials_exception  # Create new tokens
        app_logger.debug(f"Creating new tokens for user: {user.username}")
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role},
            token_version=user.token_version,
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}, token_version=user.token_version
        )
        app_logger.info(f"Tokens refreshed successfully for user: {user.username}")

        set_auth_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    except JWTError as e:
        app_logger.error(f"JWT error during token refresh: {str(e)}")
        raise credentials_exception


@router.post("/logout")
@limiter.limit("10/minute")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout a user by invalidating their tokens.

    This endpoint increments the user's token version, which invalidates
    all previously issued tokens for this user.

    Returns:
        Confirmation message
    """
    app_logger.info(f"Logout request for user: {current_user.username}")

    # Increment the token version to invalidate all existing tokens
    increment_token_version(db, current_user)

    # Clear cookies
    clear_auth_cookies(response)

    app_logger.info(f"User logged out successfully: {current_user.username}")
    return {"detail": "Successfully logged out"}
