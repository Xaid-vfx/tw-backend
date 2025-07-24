from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional

from app.routers.auth import get_current_user
from app.models.user import User
from app.models.couple import Couple
from app.schemas import CoupleCreateWithPartner, CoupleWithUsersResponse, UserResponse

router = APIRouter(prefix="/couples", tags=["couples"])

async def get_user_active_couple(user: User) -> Optional[Couple]:
    """Get the active couple for a user if it exists."""
    return await Couple.filter(
        (Couple.user1_id == user.id) | (Couple.user2_id == user.id),
        is_active=True
    ).first()

@router.post("", response_model=CoupleWithUsersResponse)
async def create_couple(
    couple_data: CoupleCreateWithPartner,
    current_user: User = Depends(get_current_user)
):
    """
    Create a couple by inviting a partner via email.
    The current user becomes user1, and the partner becomes user2.
    """
    
    # Check if current user is already in a couple
    existing_couple = await Couple.filter(
        (Couple.user1_id == current_user.id) | (Couple.user2_id == current_user.id),
        is_active=True
    ).first()
    
    if existing_couple:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in an active couple relationship"
        )
    
    # Find partner by email
    partner = await User.filter(email=couple_data.partner_email).first()
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {couple_data.partner_email} not found"
        )
    
    # Check if partner is already in a couple
    partner_existing_couple = await Couple.filter(
        (Couple.user1_id == partner.id) | (Couple.user2_id == partner.id),
        is_active=True
    ).first()
    
    
    if partner_existing_couple:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Partner {couple_data.partner_email} is already in an active couple relationship"
        )
    
    # Prevent self-coupling
    if current_user.id == partner.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot create a couple with yourself"
        )
    
    # Create the couple relationship
    couple = await Couple.create(
        user1_id=current_user.id,
        user2_id=partner.id,
        relationship_start_date=couple_data.relationship_start_date,
        is_active=True
    )
    
    # Update both users' partner_id field
    current_user.partner_id = partner.id
    partner.partner_id = current_user.id
    await current_user.save(update_fields=["partner_id"])
    await partner.save(update_fields=["partner_id"])
    
    # Return couple with user details
    return CoupleWithUsersResponse(
        id=couple.id,
        user1=UserResponse.from_orm(current_user),
        user2=UserResponse.from_orm(partner),
        relationship_start_date=couple.relationship_start_date,
        created_at=couple.created_at,
        updated_at=couple.updated_at,
        is_active=couple.is_active
    )

@router.get("/{couple_id}", response_model=CoupleWithUsersResponse)
async def get_couple(
    couple_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get couple information. Only accessible by members of the couple.
    """
    couple = await Couple.filter(id=couple_id, is_active=True).first()
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couple not found"
        )
    
    # Check if current user is part of this couple
    if current_user.id not in [couple.user1_id, couple.user2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view couples you are part of"
        )
    
    # Get user details
    user1 = await User.get(id=couple.user1_id)
    user2 = await User.get(id=couple.user2_id)
    
    return CoupleWithUsersResponse(
        id=couple.id,
        user1=UserResponse.from_orm(user1),
        user2=UserResponse.from_orm(user2),
        relationship_start_date=couple.relationship_start_date,
        created_at=couple.created_at,
        updated_at=couple.updated_at,
        is_active=couple.is_active
    )

@router.get("", response_model=List[CoupleWithUsersResponse])
async def get_user_couples(current_user: User = Depends(get_current_user)):
    """
    Get all couples that the current user is part of.
    """
    couples = await Couple.filter(
        (Couple.user1_id == current_user.id) | (Couple.user2_id == current_user.id),
        is_active=True
    )
    
    result = []
    for couple in couples:
        user1 = await User.get(id=couple.user1_id)
        user2 = await User.get(id=couple.user2_id)
        
        result.append(CoupleWithUsersResponse(
            id=couple.id,
            user1=UserResponse.from_orm(user1),
            user2=UserResponse.from_orm(user2),
            relationship_start_date=couple.relationship_start_date,
            created_at=couple.created_at,
            updated_at=couple.updated_at,
            is_active=couple.is_active
        ))
    
    return result

@router.get("/my-couple", response_model=Optional[CoupleWithUsersResponse])
async def get_my_couple(current_user: User = Depends(get_current_user)):
    """
    Get the current user's active couple if it exists.
    Returns null if user is not in a couple.
    """
    couple = await get_user_active_couple(current_user)
    if not couple:
        return None
    
    user1 = await User.get(id=couple.user1_id)
    user2 = await User.get(id=couple.user2_id)
    
    return CoupleWithUsersResponse(
        id=couple.id,
        user1=UserResponse.from_orm(user1),
        user2=UserResponse.from_orm(user2),
        relationship_start_date=couple.relationship_start_date,
        created_at=couple.created_at,
        updated_at=couple.updated_at,
        is_active=couple.is_active
    ) 