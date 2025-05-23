from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    id: UUID
    chat_id: UUID
    role: str
    content: str
    model_id: Optional[UUID] = None
    created_at: datetime
    tokens_used: int = 0
    extended_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


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


class MessageCreateSchema(BaseModel):
    chat_id: UUID
    role: str = Field(
        ..., description="Role of the message sender (e.g., 'user', 'assistant')"
    )
    content: str = Field(..., description="Content of the message")
    model_id: Optional[UUID] = None
    tokens_used: int = Field(0, description="Number of tokens used for this message")
    extended_metadata: Optional[Dict[str, Any]] = None


class ChatMessagesResponse(BaseModel):
    chat: ChatSchema
    messages: List[MessageSchema]
