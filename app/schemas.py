from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime, date

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    relationship_status: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    partner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Couple schemas
class CoupleBase(BaseModel):
    user1_id: int
    user2_id: int
    relationship_start_date: Optional[date] = None

class CoupleCreate(CoupleBase):
    pass

class CoupleResponse(CoupleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Session schemas
class SessionBase(BaseModel):
    session_type: str = Field(default="therapy", max_length=50)  # "therapy", "check-in", etc.
    session_mode: Literal["solo", "couple"] = Field(...)

class SessionCreateSolo(SessionBase):
    """Create a solo therapy session"""
    session_mode: Literal["solo"] = "solo"

class SessionCreateCouple(SessionBase):
    """Create a couple therapy session"""
    session_mode: Literal["couple"] = "couple"
    partner_email: Optional[str] = Field(None, description="Email of partner to invite")

class SessionJoin(BaseModel):
    """Join an existing session using session code"""
    session_code: str = Field(..., min_length=8, max_length=8)

class SessionUpdate(BaseModel):
    session_type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)

class SessionResponse(BaseModel):
    id: int
    session_code: str
    creator_user_id: int
    session_mode: str
    session_type: str
    couple_id: Optional[int] = None
    status: str
    max_participants: int
    current_participants: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SessionParticipantResponse(BaseModel):
    id: int
    session_id: int
    user_id: int
    role: str
    joined_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class SessionWithParticipants(SessionResponse):
    """Session with participant information"""
    participants: list[SessionParticipantResponse]

# Enhanced Message schemas for chat app
class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    sender_type: Literal["human", "ai"] = Field(...)
    message_type: str = Field(default="text", max_length=20)  # "text", "image", "file", etc.
    
class MessageCreate(MessageBase):
    session_id: int
    user_id: int  # Which user in the couple sent this message
    reply_to_message_id: Optional[int] = None  # For threading/replies

class MessageResponse(MessageBase):
    id: int
    session_id: int
    user_id: int
    reply_to_message_id: Optional[int] = None
    message_status: str = Field(default="sent")  # "sent", "delivered", "read"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# For chat conversation retrieval
class ChatConversationResponse(BaseModel):
    session_id: int
    user_id: int  # Specific user's conversation with AI
    messages: list[MessageResponse]
    total_messages: int
    
    class Config:
        from_attributes = True
