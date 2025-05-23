from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from src.auth.service import get_current_active_user
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
    """Get all chats for the current user"""
    query = db.query(Chat).filter(Chat.user_id == current_user.id)

    if not include_archived:
        query = query.filter(Chat.is_archived.is_(False))

    total = query.count()

    chats = query.order_by(Chat.updated_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "chats": chats, "skip": skip, "limit": limit}


@router.get("/{chat_id}")
async def get_chat(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific chat with all messages"""
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at)
        .all()
    )

    return {"chat": chat, "messages": messages}


@router.post("/")
async def create_chat(
    chat_data: chat_schemas.ChatCreateSchema = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new empty chat"""
    title = "New Chat"
    if chat_data and chat_data.title:
        title = chat_data.title

    chat = Chat(user_id=current_user.id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


@router.patch("/{chat_id}")
async def update_chat(
    chat_id: UUID,
    chat_update: chat_schemas.ChatUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update chat properties (title, archived status)"""
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat_update.title is not None:
        setattr(chat, "title", chat_update.title)

    if chat_update.is_archived is not None:
        setattr(chat, "is_archived", chat_update.is_archived)

    db.commit()
    db.refresh(chat)

    return chat


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a chat and all its messages"""
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Delete all messages first (can use cascade but being explicit)
    db.query(Message).filter(Message.chat_id == chat_id).delete()
    db.delete(chat)
    db.commit()

    return {"success": True}


@router.get("/models")
async def get_available_models(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Get all available models from the database"""
    models = db.query(Model).filter(Model.is_active.is_(True)).all()
    providers = db.query(ModelProvider).filter(ModelProvider.is_active.is_(True)).all()
    return {"models": models, "providers": providers}
