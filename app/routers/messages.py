from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter(prefix="/couples/{couple_id}/messages", tags=["messages"])

@router.post("")
async def send_message(couple_id: int):
    # TODO: Implement message sending logic
    return JSONResponse({"id": 1, "sender": "user1@example.com", "text": "Hello!", "timestamp": "2024-01-01T00:00:00Z"})

@router.get("")
async def get_messages(couple_id: int):
    # TODO: Implement message retrieval logic
    return JSONResponse([
        {"id": 1, "sender": "user1@example.com", "text": "Hello!", "timestamp": "2024-01-01T00:00:00Z"},
        {"id": 2, "sender": "user2@example.com", "text": "Hi!", "timestamp": "2024-01-01T00:01:00Z"}
    ]) 