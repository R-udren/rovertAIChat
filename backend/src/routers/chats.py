from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.auth.service import get_current_active_user
from src.database import get_db
from src.models.user import User
from src.schemas import chat as chat_schemas
from src.services.chat import ChatService, MessageService

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
    return ChatService.get_user_chats(
        db=db,
        user=current_user,
        skip=skip,
        limit=limit,
        include_archived=include_archived,
    )


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
    return ChatService.create_chat(db=db, user=current_user, chat_data=chat_data)


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
    return ChatService.delete_all_user_chats(db=db, user=current_user)


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
    try:
        return ChatService.get_chat_with_messages(
            db=db, user=current_user, chat_id=chat_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    try:
        return ChatService.update_chat(
            db=db, user=current_user, chat_id=chat_id, chat_update=chat_update
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    try:
        return ChatService.delete_chat(db=db, user=current_user, chat_id=chat_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/models", response_model=chat_schemas.ModelListResponse)
async def get_available_models(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """
    Get all available models from the database.

    Returns:
        A list of active models and their providers
    """
    return ChatService.get_available_models(db=db)


# Message endpoints
@router.post("/{chat_id}/messages", response_model=chat_schemas.MessageResponse)
async def create_message(
    chat_id: UUID,
    message: chat_schemas.MessageCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new message in a chat"""
    try:
        return MessageService.create_message(
            db=db, user=current_user, chat_id=chat_id, message=message
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    try:
        return MessageService.get_message(
            db=db, user=current_user, chat_id=chat_id, message_id=message_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    try:
        return MessageService.update_message(
            db=db,
            user=current_user,
            chat_id=chat_id,
            message_id=message_id,
            message_update=message_update,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


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
    try:
        return MessageService.delete_message(
            db=db, user=current_user, chat_id=chat_id, message_id=message_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    try:
        return MessageService.bulk_delete_messages(
            db=db,
            user=current_user,
            chat_id=chat_id,
            message_ids=bulk_delete.message_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
