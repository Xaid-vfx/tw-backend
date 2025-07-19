from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional

from app.models.user import User
from app.schemas import UserResponse, UserUpdate
from app.routers.auth import get_current_user
from app.services.user_service import (
    get_paginated_users,
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    check_email_exists,
    update_user_profile,
    deactivate_user,
    link_users_as_partners,
    unlink_partners,
    ensure_user_exists,
    ensure_user_is_active,
    ensure_user_can_modify,
)

router = APIRouter(prefix="/users", tags=["users"])

# Public endpoints 
@router.get("/check-email")
async def check_email_exists_endpoint(email: str = Query(..., description="Email address to check")):
    """Check if a user with the given email exists. Public endpoint."""
    exists = await check_email_exists(email)
    return {"exists": exists}

# Protected endpoints 
@router.get("/", response_model=List[UserResponse])
async def get_users_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get all users with pagination."""
    users = await get_paginated_users(skip, limit)
    return [UserResponse.from_orm(user) for user in users]

@router.get("/user-details", response_model=UserResponse)
async def get_user_details(
    current_user: User = Depends(get_current_user)
):
    """Get current user's details."""
    user = await get_user_by_id(current_user.id)
    return UserResponse.from_orm(ensure_user_exists(user))

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a user's information."""
    ensure_user_can_modify(current_user, user_id)
    
    user = await get_user_by_id(user_id)
    user = ensure_user_exists(user)
    user = ensure_user_is_active(user)
    
    updated_user = await update_user_profile(user, user_update)
    return UserResponse.from_orm(updated_user)

@router.delete("/{user_id}")
async def delete_user_endpoint(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a user account (soft delete)."""
    ensure_user_can_modify(current_user, user_id)
    
    user = await get_user_by_id(user_id)
    user = ensure_user_exists(user)
    
    await deactivate_user(user)
    return {"message": "User account deactivated successfully"}

@router.get("/search/by-username/{username}", response_model=UserResponse)
async def get_user_by_username_endpoint(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Find a user by username."""
    user = await get_user_by_username(username)
    return UserResponse.from_orm(ensure_user_exists(user))

@router.get("/search/by-email/{email}", response_model=UserResponse)
async def get_user_by_email_endpoint(
    email: str,
    current_user: User = Depends(get_current_user)
):
    """Find a user by email."""
    user = await get_user_by_email(email)
    return UserResponse.from_orm(ensure_user_exists(user))

@router.post("/{user_id}/partner/{partner_id}")
async def link_partner_endpoint(
    user_id: int,
    partner_id: int,
    current_user: User = Depends(get_current_user)
):
    """Link two users as partners."""
    ensure_user_can_modify(current_user, user_id)
    
    user = await get_user_by_id(user_id)
    user = ensure_user_exists(user)
    user = ensure_user_is_active(user)
    
    partner = await get_user_by_id(partner_id)
    partner = ensure_user_exists(partner)
    partner = ensure_user_is_active(partner)
    
    await link_users_as_partners(user, partner)
    return {"message": "Users linked as partners successfully"}

@router.delete("/{user_id}/partner")
async def unlink_partner_endpoint(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Unlink user from their partner."""
    ensure_user_can_modify(current_user, user_id)
    
    user = await get_user_by_id(user_id)
    user = ensure_user_exists(user)
    
    await unlink_partners(user)
    return {"message": "Partner unlinked successfully"}
