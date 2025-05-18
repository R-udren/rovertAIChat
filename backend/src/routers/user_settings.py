import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from src.auth.service import get_current_active_user
from src.core.logger import app_logger
from src.core.rate_limiter import limiter
from src.database import get_db
from src.models.user import User
from src.schemas.user_settings import (
    UserSettingsCreate,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from src.services.user_settings import (
    create_user_settings,
    delete_user_settings,
    get_user_settings,
    update_user_settings,
)

router = APIRouter(prefix="/api/user-settings", tags=["user-settings"])


@router.get("/me", response_model=UserSettingsResponse)
@limiter.limit("30/minute")
async def get_my_settings(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the current user's settings."""
    app_logger.debug(f"Getting settings for current user: {current_user.id}")
    settings = get_user_settings(db, uuid.UUID(str(current_user.id)))

    if not settings:
        # Auto-create settings if they don't exist
        app_logger.debug(f"Auto-creating settings for user: {current_user.id}")
        settings_data = UserSettingsCreate(
            user_id=uuid.UUID(str(current_user.id)),
            display_name=str(current_user.username),
            avatar_url=None,
        )
        settings = create_user_settings(db, settings_data)

    return settings


@router.put("/me", response_model=UserSettingsResponse)
@limiter.limit("15/minute")
async def update_my_settings(
    request: Request,
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update the current user's settings."""
    app_logger.info(f"Updating settings for current user: {current_user.id}")

    settings = get_user_settings(db, uuid.UUID(str(current_user.id)))
    if not settings:
        # Create settings if they don't exist
        app_logger.debug(f"Creating settings for user: {current_user.id}")
        settings_data = UserSettingsCreate(
            user_id=uuid.UUID(str(current_user.id)),
            **settings_update.model_dump(exclude_unset=True),
        )
        settings = create_user_settings(db, settings_data)
    else:
        # Update existing settings
        settings = update_user_settings(
            db, uuid.UUID(str(current_user.id)), settings_update
        )

    return settings


@router.get("/{user_id}", response_model=UserSettingsResponse)
async def get_user_settings_by_id(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a user's settings by user ID.
    Only admin users can access other users' settings.
    """
    if current_user.get_role() != "admin" and str(current_user.id) != str(user_id):
        app_logger.warning(
            f"Unauthorized attempt to access settings for user {user_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    settings = get_user_settings(db, user_id)
    if not settings:
        app_logger.warning(f"Settings not found for user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found",
        )

    return settings


@router.put("/{user_id}", response_model=UserSettingsResponse)
async def update_user_settings_by_id(
    user_id: uuid.UUID,
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update a user's settings by user ID.
    Only admin users can update other users' settings.
    """
    if current_user.get_role() != "admin" and str(current_user.id) != str(user_id):
        app_logger.warning(
            f"Unauthorized attempt to update settings for user {user_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    settings = update_user_settings(db, user_id, settings_update)
    if not settings:
        # Create settings if they don't exist
        app_logger.debug(f"Creating settings for user: {user_id}")
        settings_data = UserSettingsCreate(
            user_id=user_id,
            **settings_update.model_dump(exclude_unset=True),
        )
        settings = create_user_settings(db, settings_data)

    return settings


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_settings_by_id(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a user's settings by user ID.
    Only admin users can delete settings.
    """
    if current_user.get_role() != "admin":
        app_logger.warning(
            f"Unauthorized attempt to delete settings for user {user_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    success = delete_user_settings(db, user_id)
    if not success:
        app_logger.warning(f"Settings not found for user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found",
        )
