import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("guest", "user", "admin", name="user_role_enum"), default="user")
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    token_version = Column(Integer, default=1, nullable=False)

    # Relationship with UserSettings
    settings = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    chats = relationship(
        "Chat",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    model_access = relationship(
        "UserModelAccess", foreign_keys="UserModelAccess.user_id", back_populates="user"
    )

    def __str__(self):
        return f"{self.username} ({self.id}) - {self.role})"

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role}, created_at={self.created_at}, last_login={self.last_login}, is_active={self.is_active})>"

    def get_active(self):
        return self.is_active is True

    def get_role(self) -> str:
        role = self.role
        return str(role)

    def is_admin(self) -> bool:
        return self.get_role() == "admin"
