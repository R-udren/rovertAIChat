from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


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
