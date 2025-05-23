from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatSchema(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    total: int
    chats: List[ChatSchema]
    skip: int
    limit: int


class ChatCreateSchema(BaseModel):
    title: str = Field(default="New Chat")


class ChatUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    is_archived: Optional[bool] = None
