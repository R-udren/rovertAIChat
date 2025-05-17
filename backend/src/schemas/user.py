from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, Field


class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    username: str = Field(..., min_length=4, max_length=64)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=4, max_length=64)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    role: UserRole
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str
    username: Optional[str] = None
    role: Optional[str] = None


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: str


class RefreshToken(BaseModel):
    refresh_token: str
