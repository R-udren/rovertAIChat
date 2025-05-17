from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from src.auth.jwt import create_access_token, create_refresh_token, decode_token
from src.auth.service import authenticate_user, get_user_by_id, update_last_login
from src.core.logger import app_logger
from src.database import get_db
from src.schemas.user import RefreshToken, Token, UserCreate, UserResponse
from src.services.user import create_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    app_logger.info(f"Registering new user with username: {user.username}")
    db_user = create_user(db, user)
    app_logger.info(f"User registered successfully: {user.username}")
    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate and login a user.

    Args:
        form_data: OAuth2 password request form
        db: Database session

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
        )  # Update last login time
    update_last_login(db, user)

    # Create tokens
    app_logger.debug(f"Creating JWT tokens for user: {user.username}")
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    app_logger.info(f"User {user.username} logged in successfully")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token_data: RefreshToken, db: Session = Depends(get_db)
):
    """
    Refresh an access token using a refresh token.

    Args:
        refresh_token_data: The refresh token
        db: Database session

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

        if user_id is None or token_type != "refresh":
            app_logger.warning(
                "Invalid refresh token: missing sub claim or incorrect type"
            )
            raise credentials_exception

        # Get user from database (you could add more validation here)        from src.auth.service import get_user_by_id

        user = get_user_by_id(db, user_id)

        if user is None or not user.get_active():
            app_logger.warning(
                f"Invalid refresh token: user not found or inactive - {user_id}"
            )
            raise credentials_exception

        # Create new tokens
        app_logger.debug(f"Creating new tokens for user: {user.username}")
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        app_logger.info(f"Tokens refreshed successfully for user: {user.username}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    except JWTError as e:
        app_logger.error(f"JWT error during token refresh: {str(e)}")
        raise credentials_exception
