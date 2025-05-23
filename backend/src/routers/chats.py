from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.auth.service import get_current_active_user
from src.database import get_db
from src.models.chat_models import Chat, Message, Model, ModelProvider
from src.models.user import User
from src.schemas.chat import ChatListResponse

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/", response_model=ChatListResponse)
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
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Create a new empty chat"""
    chat = Chat(user_id=current_user.id, title="New Chat")
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


@router.patch("/{chat_id}")
async def update_chat(
    chat_id: UUID,
    request: Request,
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

    data = await request.json()

    if "title" in data:
        chat.title = data["title"]

    if "is_archived" in data:
        chat.is_archived = data["is_archived"]

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
