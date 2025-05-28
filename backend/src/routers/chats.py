from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.auth.service import get_current_active_user
from src.core.logger import app_logger
from src.database import get_db
from src.models.chat_models import Chat, Message, Model, ModelProvider
from src.models.user import User
from src.schemas import chat as chat_schemas

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/", response_model=chat_schemas.ChatListResponse)
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
    app_logger.debug(
        f"Getting chats for user: {current_user.id}, include_archived: {include_archived}"
    )
    query = db.query(Chat).filter(Chat.user_id == current_user.id)

    if not include_archived:
        query = query.filter(Chat.is_archived.is_(False))

    total = query.count()
    app_logger.debug(f"Found {total} chats for user {current_user.id}")

    chats = query.order_by(Chat.updated_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "chats": chats, "skip": skip, "limit": limit}


@router.get("/{chat_id}", response_model=chat_schemas.ChatMessagesResponse)
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


@router.post(
    "/", response_model=chat_schemas.ChatResponse, status_code=status.HTTP_201_CREATED
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


@router.patch("/{chat_id}", response_model=chat_schemas.ChatResponse)
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


@router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
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


@router.delete("/", status_code=status.HTTP_200_OK)
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


@router.get("/models", response_model=chat_schemas.ModelListResponse)
async def get_available_models(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """
    Get all available models from the database.

    Returns:
        A list of active models and their providers
    """
    app_logger.debug("Getting available models for chat")
    models = db.query(Model).filter(Model.is_active.is_(True)).all()
    providers = db.query(ModelProvider).filter(ModelProvider.is_active.is_(True)).all()
    app_logger.debug(f"Found {len(models)} models and {len(providers)} providers")

    return {"models": models, "providers": providers}


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
