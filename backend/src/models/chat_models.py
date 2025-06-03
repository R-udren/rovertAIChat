import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class ModelProvider(Base):
    __tablename__ = "model_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    api_url = Column(String(255), nullable=False)
    auth_type = Column(String(50), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

    # Relationships
    models = relationship("Model", back_populates="provider")
    creator = relationship("User")


class Model(Base):
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("model_providers.id"))
    name = Column(String(100), nullable=False)
    display_name = Column(String(100))
    description = Column(Text)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)

    # Relationships
    provider = relationship("ModelProvider", back_populates="models")
    messages = relationship("Message", back_populates="model")
    user_access = relationship("UserModelAccess", back_populates="model")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_archived = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"))
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    thinking = Column(
        Text, nullable=True
    )  # For assistant messages that think before responding
    tool_calls = Column(JSON, nullable=True)  # For assistant messages that call tools
    images = Column(
        JSON, nullable=True
    )  # Store base64 encoded images for multimodal models
    model_id = Column(
        UUID(as_uuid=True), ForeignKey("models.id"), nullable=True
    )  # Only for assistant messages
    created_at = Column(DateTime, default=datetime.now)
    tokens_used = Column(Integer, default=0)
    extended_metadata = Column(JSON)

    # Relationships
    chat = relationship("Chat", back_populates="messages")
    model = relationship("Model", back_populates="messages")


class UserModelAccess(Base):
    __tablename__ = "user_model_access"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"))
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    model = relationship("Model", back_populates="user_access")
    admin = relationship("User", foreign_keys=[granted_by])
