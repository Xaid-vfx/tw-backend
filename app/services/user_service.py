from fastapi import HTTPException, status
from typing import Optional, List
from tortoise.exceptions import DoesNotExist

from app.models.user import User
from app.schemas import UserResponse, UserUpdate

async def get_paginated_users(skip: int = 0, limit: int = 10) -> List[User]:
    """Get a paginated list of users."""
    return await User.all().offset(skip).limit(limit)

async def get_user_by_id(user_id: int) -> Optional[User]:
    """Get a user by their ID."""
    return await User.get_or_none(id=user_id)

async def get_user_by_email(email: str, active_only: bool = True) -> Optional[User]:
    """Get a user by their email address."""
    query = User.filter(email=email)
    if active_only:
        query = query.filter(is_active=True)
    return await query.first()

async def get_user_by_username(username: str, active_only: bool = True) -> Optional[User]:
    """Get a user by their username."""
    query = User.filter(username=username)
    if active_only:
        query = query.filter(is_active=True)
    return await query.first()

async def check_email_exists(email: str) -> bool:
    """Check if a user with the given email exists."""
    return await User.filter(email=email).exists()

async def check_username_exists(username: str) -> bool:
    """Check if a user with the given username exists."""
    return await User.filter(username=username).exists()

async def update_user_profile(user: User, update_data: UserUpdate) -> User:
    """Update a user's profile information."""
    # Check for email uniqueness if being updated
    if "email" in update_data.dict(exclude_unset=True):
        existing = await User.filter(email=update_data.email).exclude(id=user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Check for username uniqueness if being updated
    if "username" in update_data.dict(exclude_unset=True):
        existing = await User.filter(username=update_data.username).exclude(id=user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update user with provided fields
    await user.update_from_dict(update_data.dict(exclude_unset=True))
    await user.save()
    return user

async def deactivate_user(user: User) -> User:
    """Soft delete a user by setting is_active to False."""
    user.is_active = False
    await user.save()
    return user

async def link_users_as_partners(user: User, partner: User) -> tuple[User, User]:
    """Link two users as partners."""
    if user.id == partner.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot link user to themselves"
        )
    
    # Link both users
    user.partner_id = partner.id
    user.relationship_status = "in_relationship"
    await user.save()
    
    partner.partner_id = user.id
    partner.relationship_status = "in_relationship"
    await partner.save()
    
    return user, partner

async def unlink_partners(user: User) -> tuple[User, Optional[User]]:
    """Unlink a user from their partner."""
    if not user.partner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no linked partner"
        )
    
    try:
        # Get and unlink partner
        partner = await User.get(id=user.partner_id)
        partner.partner_id = None
        partner.relationship_status = "single"
        await partner.save()
        
        # Unlink user
        user.partner_id = None
        user.relationship_status = "single"
        await user.save()
        
        return user, partner
        
    except DoesNotExist:
        # Partner not found (shouldn't happen, but handle gracefully)
        user.partner_id = None
        user.relationship_status = "single"
        await user.save()
        return user, None

# Validation functions
def ensure_user_exists(user: Optional[User]) -> User:
    """Ensure a user exists or raise 404."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def ensure_user_is_active(user: User) -> User:
    """Ensure a user is active or raise 400."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is not active"
        )
    return user

def ensure_user_can_modify(current_user: User, target_user_id: int):
    """Ensure current user can modify the target user."""
    if current_user.id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this user"
        ) 