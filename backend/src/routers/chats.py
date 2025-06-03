from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.auth.service import get_current_active_user
from src.core.logger import app_logger
from src.database import get_db
from src.models.chat_models import Chat, Message
from src.models.user import User
from src.schemas import chat as chat_schemas

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/my", response_model=chat_schemas.ChatListResponse)
async def get_user_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 20,
    include_archived: bool = False,
):
    """
    Get all chats for the current user.

    Args:
        skip: Number of chats to skip for pagination
        limit: Maximum number of chats to return
        include_archived: Whether to include archived chats

    Returns:
        A paginated list of user chats
    """
    query = db.query(Chat).filter(Chat.user_id == current_user.id)

    if not include_archived:
        query = query.filter(Chat.is_archived.is_(False))

    total = query.count()
    app_logger.debug(f"Found {total} chats for user {current_user.id}")

    chats = query.order_by(Chat.updated_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "chats": chats, "skip": skip, "limit": limit}


@router.post(
    "/my",
    response_model=chat_schemas.ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat(
    chat_data: chat_schemas.ChatCreateSchema = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new empty chat.

    Args:
        chat_data: Optional data for creating the chat

    Returns:
        The created chat object
    """
    title = "New Chat"
    if chat_data and chat_data.title:
        title = chat_data.title

    app_logger.info(
        f"Creating new chat with title '{title}' for user {current_user.id}"
    )
    chat = Chat(user_id=current_user.id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    app_logger.debug(f"Created chat with ID: {chat.id}")

    return chat


@router.delete("/my", status_code=status.HTTP_200_OK)
async def delete_all_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete all chats for the current user.

    Returns:
        Success confirmation
    """
    app_logger.info(f"Deleting all chats for user {current_user.id}")
    db.query(Message).filter(Message.chat.has(user_id=current_user.id)).delete()
    db.query(Chat).filter(Chat.user_id == current_user.id).delete()
    db.commit()
    app_logger.info(f"Deleted all chats for user {current_user.id}")

    return {"success": True, "message": "All chats deleted"}


@router.get("/chat/{chat_id}", response_model=chat_schemas.ChatMessagesResponse)
async def get_chat(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific chat with all messages.

    Args:
        chat_id: UUID of the chat to retrieve

    Returns:
        The chat details and all messages in the chat

    Raises:
        HTTPException: If chat not found or not owned by user
    """
    app_logger.debug(f"Getting chat {chat_id} for user: {current_user.id}")
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        app_logger.warning(f"Chat {chat_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at)
        .all()
    )
    app_logger.debug(f"Found {len(messages)} messages for chat {chat_id}")

    return {"chat": chat, "messages": messages}


@router.patch("/chat/{chat_id}", response_model=chat_schemas.ChatResponse)
async def update_chat(
    chat_id: UUID,
    chat_update: chat_schemas.ChatUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update chat properties (title, archived status).

    Args:
        chat_id: UUID of the chat to update
        chat_update: Data for updating the chat

    Returns:
        The updated chat object

    Raises:
        HTTPException: If chat not found or not owned by user
    """
    app_logger.debug(f"Updating chat {chat_id} for user {current_user.id}")
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        app_logger.warning(f"Chat {chat_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

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
    app_logger.info(f"Updated chat {chat_id} for user {current_user.id}")

    return chat


@router.delete("/chat/{chat_id}", status_code=status.HTTP_200_OK)
async def delete_chat(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a chat and all its messages.

    Args:
        chat_id: UUID of the chat to delete

    Returns:
        Success confirmation

    Raises:
        HTTPException: If chat not found or not owned by user
    """
    app_logger.info(f"Deleting chat {chat_id} for user {current_user.id}")
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        app_logger.warning(f"Chat {chat_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    # Delete all messages first (can use cascade but being explicit)
    message_count = db.query(Message).filter(Message.chat_id == chat_id).count()
    app_logger.debug(f"Deleting {message_count} messages for chat {chat_id}")
    db.query(Message).filter(Message.chat_id == chat_id).delete()
    db.delete(chat)
    db.commit()
    app_logger.info(f"Deleted chat {chat_id} with {message_count} messages")

    return {"success": True, "message": "Chat and all messages deleted"}


@router.post("/{chat_id}/messages")
async def create_message(
    chat_id: UUID,
    message: chat_schemas.MessageCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new message in a chat"""
    # Verify chat belongs to the user
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Create the message
    db_message = Message(
        chat_id=chat_id,
        role=message.role,
        content=message.content,
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


@router.patch(
    "/{chat_id}/messages/{message_id}", response_model=chat_schemas.MessageResponse
)
async def update_message(
    chat_id: UUID,
    message_id: UUID,
    message_update: chat_schemas.MessageUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a message in a chat.

    Args:
        chat_id: UUID of the chat containing the message
        message_id: UUID of the message to update
        message_update: Data for updating the message

    Returns:
        The updated message object

    Raises:
        HTTPException: If chat or message not found, or not owned by user
    """
    app_logger.debug(
        f"Updating message {message_id} in chat {chat_id} for user {current_user.id}"
    )

    # Verify chat belongs to the user
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        app_logger.warning(f"Chat {chat_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    # Get the message and verify it belongs to the chat
    message = (
        db.query(Message)
        .filter(Message.id == message_id, Message.chat_id == chat_id)
        .first()
    )

    if not message:
        app_logger.warning(f"Message {message_id} not found in chat {chat_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    # Only allow editing user messages or prevent editing if it's an assistant message
    # You can modify this logic based on your requirements
    if message.role not in ["user"]:
        app_logger.warning(
            f"Attempt to edit non-user message {message_id} by user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only user messages can be edited",
        )

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
        f"Updated message {message_id} in chat {chat_id} for user {current_user.id}"
    )

    return message


@router.delete(
    "/{chat_id}/messages/bulk", response_model=chat_schemas.BulkMessageDeleteResponse
)
async def bulk_delete_messages(
    chat_id: UUID,
    bulk_delete: chat_schemas.BulkMessageDeleteSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete multiple messages from a chat.

    Args:
        chat_id: UUID of the chat containing the messages
        bulk_delete: Schema containing list of message IDs to delete

    Returns:
        Bulk deletion result with success count and failed deletions

    Raises:
        HTTPException: If chat not found or not owned by user
    """
    app_logger.info(
        f"Bulk deleting {len(bulk_delete.message_ids)} messages from chat {chat_id} for user {current_user.id}"
    )

    # Verify chat belongs to the user
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        app_logger.warning(f"Chat {chat_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    deleted_count = 0
    failed_deletions = []

    # Process each message ID
    for message_id in bulk_delete.message_ids:
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
                app_logger.warning(f"Message {message_id} not found in chat {chat_id}")
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


@router.delete(
    "/{chat_id}/messages/{message_id}",
    response_model=chat_schemas.MessageDeleteResponse,
)
async def delete_message(
    chat_id: UUID,
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a message from a chat.

    Args:
        chat_id: UUID of the chat containing the message
        message_id: UUID of the message to delete

    Returns:
        Success confirmation with deleted message ID

    Raises:
        HTTPException: If chat or message not found, or not owned by user
    """
    app_logger.info(
        f"Deleting message {message_id} from chat {chat_id} for user {current_user.id}"
    )

    # Verify chat belongs to the user
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        app_logger.warning(f"Chat {chat_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    # Get the message and verify it belongs to the chat
    message = (
        db.query(Message)
        .filter(Message.id == message_id, Message.chat_id == chat_id)
        .first()
    )

    if not message:
        app_logger.warning(f"Message {message_id} not found in chat {chat_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

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


@router.get(
    "/{chat_id}/messages/{message_id}", response_model=chat_schemas.MessageResponse
)
async def get_message(
    chat_id: UUID,
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific message from a chat.

    Args:
        chat_id: UUID of the chat containing the message
        message_id: UUID of the message to retrieve

    Returns:
        The requested message

    Raises:
        HTTPException: If chat or message not found, or not owned by user
    """
    app_logger.debug(
        f"Getting message {message_id} from chat {chat_id} for user {current_user.id}"
    )

    # Verify chat belongs to the user
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        app_logger.warning(f"Chat {chat_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    # Get the message and verify it belongs to the chat
    message = (
        db.query(Message)
        .filter(Message.id == message_id, Message.chat_id == chat_id)
        .first()
    )

    if not message:
        app_logger.warning(f"Message {message_id} not found in chat {chat_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    app_logger.debug(f"Retrieved message {message_id} from chat {chat_id}")
    return message
