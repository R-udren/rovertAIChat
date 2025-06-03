"""
Chat service layer for handling chat and message operations.
Separates business logic from the router layer.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from src.core.logger import app_logger
from src.models.chat_models import Chat, Message, Model, ModelProvider
from src.models.user import User
from src.schemas import chat as chat_schemas


class ChatService:
    """Service class for chat operations"""

    @staticmethod
    def get_user_chats(
        db: Session,
        user: User,
        skip: int = 0,
        limit: int = 20,
        include_archived: bool = False,
    ) -> Dict:
        """
        Get all chats for a user with pagination.

        Args:
            db: Database session
            user: User object
            skip: Number of chats to skip for pagination
            limit: Maximum number of chats to return
            include_archived: Whether to include archived chats

        Returns:
            Dictionary with total count, chats list, skip and limit
        """
        query = db.query(Chat).filter(Chat.user_id == user.id)

        if not include_archived:
            query = query.filter(Chat.is_archived.is_(False))

        total = query.count()
        app_logger.debug(f"Found {total} chats for user {user.id}")

        chats = query.order_by(Chat.updated_at.desc()).offset(skip).limit(limit).all()

        return {"total": total, "chats": chats, "skip": skip, "limit": limit}

    @staticmethod
    def create_chat(
        db: Session, user: User, chat_data: Optional[chat_schemas.ChatCreateSchema]
    ) -> Chat:
        """
        Create a new chat for a user.

        Args:
            db: Database session
            user: User object
            chat_data: Optional chat creation data

        Returns:
            Created chat object
        """
        title = "New Chat"
        if chat_data and chat_data.title:
            title = chat_data.title

        app_logger.info(f"Creating new chat with title '{title}' for user {user.id}")

        chat = Chat(user_id=user.id, title=title)
        db.add(chat)
        db.commit()
        db.refresh(chat)

        app_logger.debug(f"Created chat with ID: {chat.id}")
        return chat

    @staticmethod
    def delete_all_user_chats(db: Session, user: User) -> Dict:
        """
        Delete all chats for a user.

        Args:
            db: Database session
            user: User object

        Returns:
            Success confirmation dictionary
        """
        app_logger.info(f"Deleting all chats for user {user.id}")

        # Delete all messages first (due to foreign key constraints)
        db.query(Message).filter(Message.chat.has(user_id=user.id)).delete()
        # Delete all chats
        db.query(Chat).filter(Chat.user_id == user.id).delete()
        db.commit()

        app_logger.info(f"Deleted all chats for user {user.id}")
        return {"success": True, "message": "All chats deleted"}

    @staticmethod
    def get_chat_with_messages(db: Session, user: User, chat_id: UUID) -> Dict:
        """
        Get a specific chat with all its messages.

        Args:
            db: Database session
            user: User object
            chat_id: UUID of the chat to retrieve

        Returns:
            Dictionary with chat and messages

        Raises:
            ValueError: If chat not found or not owned by user
        """
        app_logger.debug(f"Getting chat {chat_id} for user: {user.id}")

        chat = (
            db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
        )

        if not chat:
            app_logger.warning(f"Chat {chat_id} not found for user {user.id}")
            raise ValueError("Chat not found")

        messages = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at)
            .all()
        )

        app_logger.debug(f"Found {len(messages)} messages for chat {chat_id}")
        return {"chat": chat, "messages": messages}

    @staticmethod
    def update_chat(
        db: Session,
        user: User,
        chat_id: UUID,
        chat_update: chat_schemas.ChatUpdateSchema,
    ) -> Chat:
        """
        Update chat properties.

        Args:
            db: Database session
            user: User object
            chat_id: UUID of the chat to update
            chat_update: Update data

        Returns:
            Updated chat object

        Raises:
            ValueError: If chat not found or not owned by user
        """
        app_logger.debug(f"Updating chat {chat_id} for user {user.id}")

        chat = (
            db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
        )

        if not chat:
            app_logger.warning(f"Chat {chat_id} not found for user {user.id}")
            raise ValueError("Chat not found")

        updates = {}
        if chat_update.title is not None:
            setattr(chat, "title", chat_update.title)
            updates["title"] = chat_update.title

        if chat_update.is_archived is not None:
            setattr(chat, "is_archived", chat_update.is_archived)
            updates["is_archived"] = chat_update.is_archived

        app_logger.debug(f"Updating chat {chat_id} with data: {updates}")
        db.commit()
        db.refresh(chat)
        app_logger.info(f"Updated chat {chat_id} for user {user.id}")

        return chat

    @staticmethod
    def delete_chat(db: Session, user: User, chat_id: UUID) -> Dict:
        """
        Delete a chat and all its messages.

        Args:
            db: Database session
            user: User object
            chat_id: UUID of the chat to delete

        Returns:
            Success confirmation dictionary

        Raises:
            ValueError: If chat not found or not owned by user
        """
        app_logger.info(f"Deleting chat {chat_id} for user {user.id}")

        chat = (
            db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
        )

        if not chat:
            app_logger.warning(f"Chat {chat_id} not found for user {user.id}")
            raise ValueError("Chat not found")

        # Delete all messages first (can use cascade but being explicit)
        message_count = db.query(Message).filter(Message.chat_id == chat_id).count()
        app_logger.debug(f"Deleting {message_count} messages for chat {chat_id}")

        db.query(Message).filter(Message.chat_id == chat_id).delete()
        db.delete(chat)
        db.commit()

        app_logger.info(f"Deleted chat {chat_id} with {message_count} messages")
        return {"success": True, "message": "Chat and all messages deleted"}

    @staticmethod
    def get_available_models(db: Session) -> Dict:
        """
        Get all available models and providers.

        Args:
            db: Database session

        Returns:
            Dictionary with models and providers lists
        """
        app_logger.debug("Getting available models for chat")

        models = db.query(Model).filter(Model.is_active.is_(True)).all()
        providers = (
            db.query(ModelProvider).filter(ModelProvider.is_active.is_(True)).all()
        )

        app_logger.debug(f"Found {len(models)} models and {len(providers)} providers")
        return {"models": models, "providers": providers}


class MessageService:
    """Service class for message operations"""

    @staticmethod
    def create_message(
        db: Session,
        user: User,
        chat_id: UUID,
        message: chat_schemas.MessageCreateSchema,
    ) -> Message:
        """
        Create a new message in a chat.

        Args:
            db: Database session
            user: User object
            chat_id: UUID of the chat
            message: Message data

        Returns:
            Created message object

        Raises:
            ValueError: If chat not found or not owned by user
        """
        # Verify chat belongs to the user
        chat = (
            db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
        )

        if not chat:
            raise ValueError("Chat not found")

        # Create the message
        db_message = Message(
            chat_id=chat_id,
            role=message.role,
            content=message.content,
            images=message.images,
            model_id=message.model_id,
            tokens_used=message.tokens_used,
            extended_metadata=message.extended_metadata,
        )

        # Update the chat's last activity timestamp
        setattr(chat, "updated_at", datetime.now())

        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        return db_message

    @staticmethod
    def get_message(
        db: Session, user: User, chat_id: UUID, message_id: UUID
    ) -> Message:
        """
        Get a specific message from a chat.

        Args:
            db: Database session
            user: User object
            chat_id: UUID of the chat
            message_id: UUID of the message

        Returns:
            Message object

        Raises:
            ValueError: If chat or message not found, or not owned by user
        """
        app_logger.debug(
            f"Getting message {message_id} from chat {chat_id} for user {user.id}"
        )

        # Verify chat belongs to the user
        chat = (
            db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
        )

        if not chat:
            app_logger.warning(f"Chat {chat_id} not found for user {user.id}")
            raise ValueError("Chat not found")

        # Get the message and verify it belongs to the chat
        message = (
            db.query(Message)
            .filter(Message.id == message_id, Message.chat_id == chat_id)
            .first()
        )

        if not message:
            app_logger.warning(f"Message {message_id} not found in chat {chat_id}")
            raise ValueError("Message not found")

        app_logger.debug(f"Retrieved message {message_id} from chat {chat_id}")
        return message

    @staticmethod
    def update_message(
        db: Session,
        user: User,
        chat_id: UUID,
        message_id: UUID,
        message_update: chat_schemas.MessageUpdateSchema,
    ) -> Message:
        """
        Update a message in a chat.

        Args:
            db: Database session
            user: User object
            chat_id: UUID of the chat
            message_id: UUID of the message
            message_update: Update data

        Returns:
            Updated message object

        Raises:
            ValueError: If chat or message not found, or not owned by user
            PermissionError: If trying to edit non-user message
        """
        app_logger.debug(
            f"Updating message {message_id} in chat {chat_id} for user {user.id}"
        )

        # Verify chat belongs to the user
        chat = (
            db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
        )

        if not chat:
            app_logger.warning(f"Chat {chat_id} not found for user {user.id}")
            raise ValueError("Chat not found")

        # Get the message and verify it belongs to the chat
        message = (
            db.query(Message)
            .filter(Message.id == message_id, Message.chat_id == chat_id)
            .first()
        )

        if not message:
            app_logger.warning(f"Message {message_id} not found in chat {chat_id}")
            raise ValueError("Message not found")

        # Only allow editing user messages
        if message.role not in ["user"]:
            app_logger.warning(
                f"Attempt to edit non-user message {message_id} by user {user.id}"
            )
            raise PermissionError("Only user messages can be edited")

        # Update the message fields
        updates = {}
        if message_update.content is not None:
            setattr(message, "content", message_update.content)
            updates["content"] = message_update.content

        if message_update.images is not None:
            setattr(message, "images", message_update.images)
            updates["images"] = message_update.images

        if message_update.extended_metadata is not None:
            setattr(message, "extended_metadata", message_update.extended_metadata)
            updates["extended_metadata"] = message_update.extended_metadata

        # Update the chat's last activity timestamp
        setattr(chat, "updated_at", datetime.now())

        app_logger.debug(f"Updating message {message_id} with data: {updates}")
        db.commit()
        db.refresh(message)
        app_logger.info(
            f"Updated message {message_id} in chat {chat_id} for user {user.id}"
        )

        return message

    @staticmethod
    def delete_message(
        db: Session, user: User, chat_id: UUID, message_id: UUID
    ) -> Dict:
        """
        Delete a message from a chat.

        Args:
            db: Database session
            user: User object
            chat_id: UUID of the chat
            message_id: UUID of the message

        Returns:
            Success confirmation dictionary

        Raises:
            ValueError: If chat or message not found, or not owned by user
        """
        app_logger.info(
            f"Deleting message {message_id} from chat {chat_id} for user {user.id}"
        )

        # Verify chat belongs to the user
        chat = (
            db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
        )

        if not chat:
            app_logger.warning(f"Chat {chat_id} not found for user {user.id}")
            raise ValueError("Chat not found")

        # Get the message and verify it belongs to the chat
        message = (
            db.query(Message)
            .filter(Message.id == message_id, Message.chat_id == chat_id)
            .first()
        )

        if not message:
            app_logger.warning(f"Message {message_id} not found in chat {chat_id}")
            raise ValueError("Message not found")

        # Store message ID for response
        deleted_id = message.id

        # Delete the message
        db.delete(message)

        # Update the chat's last activity timestamp
        setattr(chat, "updated_at", datetime.now())

        db.commit()
        app_logger.info(f"Deleted message {deleted_id} from chat {chat_id}")

        return {
            "success": True,
            "message": "Message deleted successfully",
            "deleted_message_id": deleted_id,
        }

    @staticmethod
    def bulk_delete_messages(
        db: Session, user: User, chat_id: UUID, message_ids: List[UUID]
    ) -> Dict:
        """
        Delete multiple messages from a chat.

        Args:
            db: Database session
            user: User object
            chat_id: UUID of the chat
            message_ids: List of message IDs to delete

        Returns:
            Bulk deletion result dictionary

        Raises:
            ValueError: If chat not found or not owned by user
        """
        app_logger.info(
            f"Bulk deleting {len(message_ids)} messages from chat {chat_id} for user {user.id}"
        )

        # Verify chat belongs to the user
        chat = (
            db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
        )

        if not chat:
            app_logger.warning(f"Chat {chat_id} not found for user {user.id}")
            raise ValueError("Chat not found")

        deleted_count = 0
        failed_deletions = []

        # Process each message ID
        for message_id in message_ids:
            try:
                # Get the message and verify it belongs to the chat
                message = (
                    db.query(Message)
                    .filter(Message.id == message_id, Message.chat_id == chat_id)
                    .first()
                )

                if message:
                    db.delete(message)
                    deleted_count += 1
                    app_logger.debug(f"Queued message {message_id} for deletion")
                else:
                    app_logger.warning(
                        f"Message {message_id} not found in chat {chat_id}"
                    )
                    failed_deletions.append(message_id)

            except Exception as e:
                app_logger.error(f"Error deleting message {message_id}: {str(e)}")
                failed_deletions.append(message_id)

        # Update the chat's last activity timestamp if any messages were deleted
        if deleted_count > 0:
            setattr(chat, "updated_at", datetime.now())

        # Commit all deletions at once
        db.commit()

        app_logger.info(
            f"Bulk deleted {deleted_count} messages from chat {chat_id}, {len(failed_deletions)} failed"
        )

        return {
            "success": True,
            "message": f"Deleted {deleted_count} messages, {len(failed_deletions)} failed",
            "deleted_count": deleted_count,
            "failed_deletions": failed_deletions,
        }
