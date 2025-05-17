import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.auth.jwt import get_password_hash
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        user: User creation data

    Returns:
        Newly created user

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        id=uuid.uuid4(),
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user(db: Session, user_id: uuid.UUID) -> User:
    """Get a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get a list of users."""
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: uuid.UUID, user_update: UserUpdate) -> User:
    """Update a user's information."""
    db_user = get_user(db, user_id)

    # Update fields if provided
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user


def deactivate_user(db: Session, user_id: uuid.UUID) -> User:
    """Deactivate a user (soft delete)."""
    db_user = get_user(db, user_id)
    db_user.is_active = db_user.is_active.expression.false()

    db.commit()
    db.refresh(db_user)

    return db_user


def activate_user(db: Session, user_id: uuid.UUID) -> User:
    """Activate a deactivated user."""
    db_user = get_user(db, user_id)
    db_user.is_active = db_user.is_active.expression.true()

    db.commit()
    db.refresh(db_user)

    return db_user
