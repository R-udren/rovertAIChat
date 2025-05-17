import uuid
from typing import Optional
from sqlalchemy.orm import Session

from src.core.logger import app_logger
from src.models.user_settings import UserSettings
from src.schemas.user_settings import UserSettingsCreate, UserSettingsUpdate


def get_user_settings(db: Session, user_id: uuid.UUID) -> Optional[UserSettings]:
    """Get user settings by user ID."""
    app_logger.debug(f"Getting settings for user: {user_id}")
    return db.query(UserSettings).filter(UserSettings.user_id == user_id).first()


def create_user_settings(db: Session, settings: UserSettingsCreate) -> UserSettings:
    """Create user settings."""
    app_logger.info(f"Creating settings for user: {settings.user_id}")

    # Check if settings already exist
    existing_settings = get_user_settings(db, settings.user_id)
    if existing_settings:
        app_logger.warning(f"Settings already exist for user: {settings.user_id}")
        return existing_settings

    # Create settings
    db_settings = UserSettings(
        user_id=settings.user_id,
        default_model_id=settings.default_model_id,
        display_name=settings.display_name,
        avatar_url=settings.avatar_url,
        preferences=settings.preferences,
    )

    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    app_logger.info(f"Settings created for user: {settings.user_id}")

    return db_settings


def update_user_settings(
    db: Session, user_id: uuid.UUID, settings_update: UserSettingsUpdate
) -> Optional[UserSettings]:
    """Update user settings."""
    app_logger.info(f"Updating settings for user: {user_id}")

    db_settings = get_user_settings(db, user_id)
    if not db_settings:
        app_logger.warning(f"No settings found for user: {user_id}")
        return None

    # Update fields if provided
    update_data = settings_update.model_dump(exclude_unset=True)
    app_logger.debug(f"Updating settings fields: {update_data}")

    for key, value in update_data.items():
        setattr(db_settings, key, value)

    db.commit()
    db.refresh(db_settings)
    app_logger.info(f"Settings updated for user: {user_id}")

    return db_settings


def delete_user_settings(db: Session, user_id: uuid.UUID) -> bool:
    """Delete user settings."""
    app_logger.info(f"Deleting settings for user: {user_id}")

    db_settings = get_user_settings(db, user_id)
    if not db_settings:
        app_logger.warning(f"No settings found for user: {user_id}")
        return False

    db.delete(db_settings)
    db.commit()
    app_logger.info(f"Settings deleted for user: {user_id}")

    return True
