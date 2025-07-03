import string

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter(prefix="/couples/{couple_id}/messages", tags=["messages"])


def construct_prompt(couple_id: int, message: str):
    """
    Construct the prompt for the AI model using:
    - System prompt
    - RAG (Retrieval Augmented Generation) context
    - Last 2-3 chat summaries
    - Current user input
    """
    # TODO: Implement system prompt + RAG + last 2-3 chats summary + user input
    pass


@router.post("")
async def send_message(couple_id: int, message: str):
    # TODO: Send message method will call construct_prompt, which will call the RAG and generate the prompt
    construct_prompt(couple_id, message)
    return JSONResponse({"status": "Message processed (placeholder)"})

@router.get("")
async def get_messages(couple_id: int):
    # TODO: Implement message retrieval logic
    return JSONResponse([
        {"id": 1, "sender": "user1@example.com", "text": "Hello!", "timestamp": "2024-01-01T00:00:00Z"},
        {"id": 2, "sender": "user2@example.com", "text": "Hi!", "timestamp": "2024-01-01T00:01:00Z"}
    ]) 