import string
import os
from dotenv import load_dotenv

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from mem0 import MemoryClient
from anthropic import Anthropic

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/couples/{couple_id}/messages", tags=["messages"])

# Initialize mem0 client for AI agents
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

# Initialize Anthropic client for Claude 3 Haiku
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def get_couple_ai_agent(couple_id: int) -> str:
    return f"couple_{couple_id}"


def construct_prompt(message: str, memories: List[Dict[str, Any]]):

    system_prompt = """You are an AI couples therapy assistant. Your role is to:
1. Help couples communicate better and understand each other
2. Provide empathetic and constructive responses
3. Use context from their conversation history to give personalized advice
4. Encourage healthy communication patterns
5. Help resolve conflicts and misunderstandings

Always be supportive, non-judgmental, and focus on improving their relationship."""

    # Extract relevant context from memories
    memory_context = []
    for memory in memories:
        if isinstance(memory, dict) and 'memory' in memory:
            memory_context.append(memory['memory'])

    rag_context = "\n".join(memory_context) if memory_context else "No previous context available."

    full_prompt = f"""System: {system_prompt}

Previous Context:
{rag_context}

User Message: {message}

Assistant:"""

    return full_prompt


def call_llm(full_prompt):
    try:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        )
        
        # Extract text content from the response
        if response.content and len(response.content) > 0:
            content_block = response.content[0]
            if hasattr(content_block, 'text'):
                return content_block.text
            else:
                return str(content_block)
        else:
            return "I apologize, but I received an empty response. Please try again."
            
    except Exception as e:
        print(f"Error calling Claude 3 Haiku: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later."


class SendMessageRequest(BaseModel):
    message: str
    sender_id: Optional[str] = None  # Optional: to track who sent the message


@router.post("")
async def send_message(couple_id: int, request: SendMessageRequest):
    couple_agent = get_couple_ai_agent(couple_id)

    client.add([{"role": "user", "content": request.message}], user_id=couple_agent)

    memories = client.search(request.message, user_id=couple_agent)
    print(f"Relevant memories for couple {couple_id}: {len(memories)} found")

    prompt_data = construct_prompt(request.message, memories)

    ai_response = call_llm(prompt_data)

    client.add([{"role": "assistant", "content": ai_response}], user_id=couple_agent)

    return JSONResponse({
        "couple_agent": couple_agent,
        "user_message": request.message,
        "sender_id": request.sender_id,
        "ai_response": ai_response,
        "prompt_data": prompt_data,
        "memories_used": len(memories)
    })


@router.get("")
async def get_messages(couple_id: int):
    # TODO: Implement message retrieval logic
    return JSONResponse([
        {"id": 1, "sender": "user1@example.com", "text": "Hello!", "timestamp": "2024-01-01T00:00:00Z"},
        {"id": 2, "sender": "user2@example.com", "text": "Hi!", "timestamp": "2024-01-01T00:01:00Z"}
    ])
