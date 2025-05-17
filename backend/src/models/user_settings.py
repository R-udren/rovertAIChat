from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from src.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(UUID(), ForeignKey("users.id"), primary_key=True)
    default_model_id = Column(UUID(), nullable=True)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    preferences = Column(JSON, nullable=True)

    # Define relationship with User
    user = relationship("User", back_populates="settings", uselist=False)

    def __repr__(self):
        return (
            f"<UserSettings(user_id={self.user_id}, display_name={self.display_name})>"
        )
