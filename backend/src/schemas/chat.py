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
    chat_id: UUID
    role: str = Field(
        ..., description="Role of the message sender (e.g., 'user', 'assistant')"
    )
    content: str = Field(..., description="Content of the message")
    model_id: Optional[UUID] = None
    tokens_used: int = Field(0, description="Number of tokens used for this message")
    extended_metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Response schema for a message"""

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
    role: str = Field(
        ..., description="Role of the message sender (e.g., 'user', 'assistant')"
    )
    content: str = Field(..., description="Content of the message")


class OllamaChatRequest(BaseModel):
    model: str = Field(..., description="Name of the Ollama model to use")
    messages: List[ChatMessage] = Field(
        ..., description="List of conversation messages"
    )
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    options: Optional[Dict[str, Any]] = Field(
        None, description="Additional model options"
    )
    chatId: UUID = Field(..., description="ID of the chat this message belongs to")


class ModelDetails(BaseModel):
    """Schema for model details within a tag response."""

    parent_model: str
    format: str
    family: str
    families: List[str]
    parameter_size: str
    quantization_level: str


class OllamaModel(BaseModel):
    """Schema for individual Ollama model in tags response."""

    name: str
    model: str
    modified_at: datetime
    size: int
    digest: str
    details: ModelDetails


class OllamaTagsResponse(BaseModel):
    """Schema for Ollama tags API response."""

    models: List[OllamaModel]
