from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from tortoise.exceptions import DoesNotExist

from app.models.user import User
from app.schemas import UserResponse, UserUpdate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get all users with pagination."""
    users = await User.all().offset(skip).limit(limit)
    return [UserResponse.from_orm(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific user by ID."""
    try:
        user = await User.get(id=user_id)
        return UserResponse.from_orm(user)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a user's information."""
    # Check if user is updating their own profile or has admin privileges
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    try:
        user = await User.get(id=user_id)
        
        # Update only provided fields
        update_data = user_update.dict(exclude_unset=True)
        
        # Check for email/username uniqueness if being updated
        if "email" in update_data:
            existing_email = await User.filter(email=update_data["email"]).exclude(id=user_id).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
        
        if "username" in update_data:
            existing_username = await User.filter(username=update_data["username"]).exclude(id=user_id).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Update user
        await user.update_from_dict(update_data)
        await user.save()
        
        return UserResponse.from_orm(user)
        
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a user account (soft delete by setting is_active=False)."""
    # Check if user is deleting their own account or has admin privileges
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    try:
        user = await User.get(id=user_id)
        
        # Soft delete by setting is_active to False
        user.is_active = False
        await user.save()
        
        return {"message": "User account deactivated successfully"}
        
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.get("/search/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Find a user by username."""
    user = await User.filter(username=username, is_active=True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)

@router.get("/search/by-email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    current_user: User = Depends(get_current_user)
):
    """Find a user by email."""
    user = await User.filter(email=email, is_active=True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)

@router.post("/{user_id}/partner/{partner_id}")
async def link_partner(
    user_id: int,
    partner_id: int,
    current_user: User = Depends(get_current_user)
):
    """Link two users as partners."""
    # Check if user is linking their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to link this user"
        )
    
    if user_id == partner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot link user to themselves"
        )
    
    try:
        user = await User.get(id=user_id)
        partner = await User.get(id=partner_id)
        
        # Link the users
        user.partner_id = partner_id
        user.relationship_status = "in_relationship"
        await user.save()
        
        partner.partner_id = user_id
        partner.relationship_status = "in_relationship"
        await partner.save()
        
        return {"message": "Users linked as partners successfully"}
        
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or partner not found"
        )

@router.delete("/{user_id}/partner")
async def unlink_partner(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Unlink user from their partner."""
    # Check if user is unlinking their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to unlink this user"
        )
    
    try:
        user = await User.get(id=user_id)
        
        if user.partner_id:
            # Unlink partner
            partner = await User.get(id=user.partner_id)
            partner.partner_id = None
            partner.relationship_status = "single"
            await partner.save()
            
            # Unlink user
            user.partner_id = None
            user.relationship_status = "single"
            await user.save()
            
            return {"message": "Partner unlinked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no linked partner"
            )
            
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
