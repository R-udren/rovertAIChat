from typing import Any, Dict, Optional

from pydantic import UUID4, BaseModel, Field
from src.schemas.user import UserResponse


class UserSettingsBase(BaseModel):
    default_model_id: Optional[UUID4] = None
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
    preferences: Optional[Dict[str, Any]] = None


class UserSettingsCreate(UserSettingsBase):
    user_id: UUID4


class UserSettingsUpdate(UserSettingsBase):
    pass


class UserSettingsInDB(UserSettingsBase):
    user_id: UUID4

    class Config:
        from_attributes = True


class UserSettingsResponse(UserSettingsInDB):
    pass


class UserWithSettings(UserResponse):
    settings: Optional[UserSettingsResponse] = None
