import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.service import get_current_active_user
from src.database import get_db
from src.models.user import User
from src.schemas.user import UserResponse, UserUpdate
from src.services.user import (
    activate_user,
    deactivate_user,
    get_user,
    get_users,
    update_user,
)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get the currently authenticated user."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update the current user's information."""
    return update_user(db, uuid.UUID(str(current_user.id)), user_update)


@router.get("", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a list of users.
    Only admin users can access this endpoint.
    """
    if current_user.get_role() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a user by ID.
    Users can only access their own user info, admins can access any.
    """
    if current_user.get_role() != "admin" and str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return get_user(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update a user's information.
    Only admin users can update other users.
    """
    if current_user.get_role().__str__ != "admin" and str(current_user.id) != str(
        user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return update_user(db, user_id, user_update)


@router.delete("/{user_id}", response_model=UserResponse)
async def deactivate_user_endpoint(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Deactivate a user (soft delete).
    Only admin users can deactivate users.
    """
    if current_user.get_role() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return deactivate_user(db, user_id)


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user_endpoint(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Activate a deactivated user.
    Only admin users can activate users.
    """
    if current_user.get_role() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return activate_user(db, user_id)
