from fastapi import APIRouter, Depends, HTTPException, status
from typing import Union

from app.routers.auth import get_current_user
from app.models.user import User
from app.schemas import (
    SessionCreateSolo,
    SessionCreateCouple,
    SessionJoin,
    SessionResponse,
    SessionWithParticipants,
)
from app.services.session_service import (
    get_active_session_for_user,
    check_user_active_session,
    create_new_session,
    get_session_by_code,
    add_participant_to_session,
    ensure_session_exists,
    ensure_session_has_capacity,
    ensure_user_not_in_session,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Return the active session (if any) that the current user is part of.
@router.get("/get-session", response_model=SessionWithParticipants)
async def get_session(
    current_user: User = Depends(get_current_user),
):

    session = await get_active_session_for_user(current_user)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session

# Check if user already has a session
# Create new session
@router.post("/create-session", response_model=SessionWithParticipants)
async def create_session(
    session_data: Union[SessionCreateSolo, SessionCreateCouple],
    current_user: User = Depends(get_current_user),
):

    existing = await check_user_active_session(current_user)
    ensure_user_not_in_session(existing)
    
    session = await create_new_session(session_data, current_user)
    return session  # Now returns SessionWithParticipants


# Check if user already has a session
# Join an existing session using its 8-character code.
# Add user to session
@router.post("/join-session", response_model=SessionResponse)
async def join_session(
    join_data: SessionJoin,
    current_user: User = Depends(get_current_user),
):
        
    existing = await check_user_active_session(current_user)
    ensure_user_not_in_session(existing)
    

    session = await get_session_by_code(join_data.session_code)
    session = ensure_session_exists(session) 
    ensure_session_has_capacity(session)     
    

    session = await add_participant_to_session(session, current_user)  
    return SessionResponse.from_orm(session)