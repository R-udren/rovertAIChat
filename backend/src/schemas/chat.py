from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    id: UUID
    chat_id: UUID
    role: str
    content: str
    images: Optional[List[str]] = None  # List of base64 encoded images
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


class ChatResponse(BaseModel):
    """Response schema for a single chat"""

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
    role: str = Field(
        ..., description="Role of the message sender (e.g., 'user', 'assistant')"
    )
    content: str = Field(..., description="Content of the message")
    images: Optional[List[str]] = Field(
        None, description="List of base64 encoded images"
    )


class MessageUpdateSchema(BaseModel):
    """Schema for updating a message"""

    content: Optional[str] = Field(
        None, min_length=1, description="Updated content of the message"
    )
    images: Optional[List[str]] = Field(
        None, description="Updated list of base64 encoded images"
    )
    extended_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Updated metadata"
    )


class MessageDeleteResponse(BaseModel):
    """Response schema for message deletion"""

    success: bool
    message: str
    deleted_message_id: UUID


class BulkMessageDeleteSchema(BaseModel):
    """Schema for bulk message deletion"""

    message_ids: List[UUID] = Field(..., description="List of message IDs to delete")


class BulkMessageDeleteResponse(BaseModel):
    """Response schema for bulk message deletion"""

    success: bool
    message: str
    deleted_count: int
    failed_deletions: List[UUID] = Field(
        default_factory=list, description="Message IDs that failed to delete"
    )


class MessageResponse(BaseModel):
    """Response schema for a message"""

    id: UUID
    chat_id: UUID
    role: str
    content: str
    images: Optional[List[str]] = None  # List of base64 encoded images
    model_id: Optional[UUID] = None
    created_at: datetime
    tokens_used: int = 0
    extended_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ChatMessagesResponse(BaseModel):
    chat: ChatSchema
    messages: List[MessageSchema]


class ModelResponse(BaseModel):
    """Response schema for a model"""

    id: UUID
    name: str
    provider_id: UUID
    is_active: bool
    max_tokens: int
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ModelProviderResponse(BaseModel):
    """Response schema for a model provider"""

    id: UUID
    name: str
    is_active: bool
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    """Response schema for the list of available models"""

    models: List[ModelResponse]
    providers: List[ModelProviderResponse]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "tool"] = Field(
        ...,
        description="Role of the message sender (e.g., 'user', 'assistant')",
        examples=["user", "assistant", "system", "tool"],
    )
    content: str = Field(
        ..., description="Content of the message", examples=["Hello, how are you?"]
    )
    thinking: Optional[str] = Field(
        None,
        description="Thinking process of the model before responding",
        examples=["Let me think about that..."],
    )
    images: Optional[List[str]] = Field(
        None,
        description="List of base64 encoded images for multimodal models",
        examples=[],
    )
