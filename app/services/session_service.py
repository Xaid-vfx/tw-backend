from fastapi import HTTPException, status
from typing import Optional, List

from app.models.session import Session
from app.models.session_participant import SessionParticipant
from app.models.user import User
from app.schemas import (
    SessionCreateSolo,
    SessionCreateCouple,
    SessionResponse,
    SessionParticipantResponse,
    SessionWithParticipants
)

async def get_active_session_for_user(user: User) -> Optional[SessionWithParticipants]:
    """Get the active session for a user if it exists."""
    participant = await SessionParticipant.filter(user_id=user.id, is_active=True).first()
    if not participant:
        return None

    session = await Session.get(id=participant.session_id)
    participants_qs = await SessionParticipant.filter(session_id=session.id, is_active=True)
    participants = [SessionParticipantResponse.from_orm(p) for p in participants_qs]

    session_resp = SessionResponse.from_orm(session)
    return SessionWithParticipants(**session_resp.model_dump(), participants=participants)

async def check_user_active_session(user: User) -> Optional[SessionParticipant]:
    """Check if user has an active session."""
    return await SessionParticipant.filter(user_id=user.id, is_active=True).first()

async def create_new_session(
    session_data: SessionCreateSolo | SessionCreateCouple,
    creator: User
) -> SessionWithParticipants:
    """Create a new session and register the creator as first participant."""
    
    # Basic business rules
    session_mode = session_data.session_mode
    max_participants = 2

    session = await Session.create(
        session_code=Session.generate_session_code(),
        creator_user_id=creator.id, 
        session_mode=session_mode,
        couple_id=None,  # Filled later for couple sessions if needed
        max_participants=max_participants,
        current_participants=1,
    )

    # Register the creator as the first participant
    await SessionParticipant.create(
        session_id=session.id,
        user_id=creator.id,
        role="creator",
    )

    # Return full session details with participants
    participants_qs = await SessionParticipant.filter(session_id=session.id, is_active=True)
    participants = [SessionParticipantResponse.from_orm(p) for p in participants_qs]
    
    session_resp = SessionResponse.from_orm(session)
    return SessionWithParticipants(**session_resp.model_dump(), participants=participants)

async def get_session_by_code(session_code: str) -> Optional[Session]:
    """Get a session by its unique code."""
    return await Session.filter(session_code=session_code).first()

async def add_participant_to_session(
    session: Session,
    user: User,
) -> Session:
    """Add a user as participant to a session."""
    
    # Add user as participant
    await SessionParticipant.create(
        session_id=session.id,
        user_id=user.id,
        role="participant",
    )

    # Increment participant count safely
    session.current_participants += 1
    await session.save(update_fields=["current_participants"])

    return session

# Error checking functions
def ensure_session_exists(session: Optional[Session]) -> Session:
    """Ensure a session exists or raise 404."""
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session

def ensure_session_has_capacity(session: Session):
    """Ensure session isn't full."""
    if session.current_participants >= session.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is full"
        )

def ensure_user_not_in_session(participant: Optional[SessionParticipant]):
    """Ensure user isn't already in a session."""
    if participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active session"
        ) 