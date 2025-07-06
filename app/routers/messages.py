import string
import os
from dotenv import load_dotenv
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks
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


def log_message(level: str, message: str):
    """Helper function to log messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def get_couple_ai_agent(couple_id: int) -> str:
    return f"couple_{couple_id}"


def construct_prompt(message: str, memories: List[Dict[str, Any]], partner: Optional[str] = None):

    system_prompt = """You are an AI couples therapy assistant.
Your role:
- Prioritize listening and emotional validation before giving advice.
- Reflect the user’s feelings and intentions, then gently offer perspective if needed.
- Use prior conversation history (specific to the current partner) to remember relationship dynamics.
- Be warm, supportive, and non-judgmental.
- Let the user lead; suggest only after emotional cues are heard and acknowledged.
- Avoid repeating your identity or stating your role in responses.
- When a user shares pride, joy, or success, **stay with that emotion first** — celebrate and explore before shifting to relationship matters (unless they initiate).
- Avoid therapist jargon. Use natural, compassionate, human-like language.
- Keep Partner A and Partner B’s context separate — never mix memories or cross-address.
- Use CBT principles: observe thoughts, emotions, and behaviors gently.
- Tone should always prioritize connection, empathy, and curiosity.

Response approach:
1. **Hear** the user and reflect their current message.
2. **Validate** or empathize with their emotional experience.
3. **If appropriate**, gently guide or explore further.

Never include meta-instructions or label your response structure. Speak like a grounded, present listener.
"""

    # Add partner context if available
    partner_context = ""
    if partner:
        partner_context = f"\nCurrent Speaker: Partner {partner}"
        system_prompt += f"\n\nNote: The current message is from Partner {partner}. Consider their perspective and any patterns in their communication style from previous conversations."

    # Extract memory context
    memory_context = []
    for memory in memories:
        if isinstance(memory, dict) and 'memory' in memory:
            memory_context.append(memory['memory'])

    rag_context = "\n".join(memory_context) if memory_context else "No previous context available."

    full_prompt = f"""System: {system_prompt}{partner_context}

Context from Past Conversations:
{rag_context}

New Message from User:
\"\"\"{message}\"\"\"

Therapist's Response:
"""
    print(full_prompt)
    return full_prompt


def call_llm(full_prompt):
    try:
        log_message("LLM", "Sending request to Claude 3 Haiku...")
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
        
        log_message("LLM", "Received response from Claude 3 Haiku")
        
        # Extract text content from the response
        if response.content and len(response.content) > 0:
            content_block = response.content[0]
            if hasattr(content_block, 'text'):
                log_message("LLM", "✅ Successfully extracted text from response")
                return content_block.text
            else:
                log_message("LLM", f"⚠️ Unexpected content block type: {type(content_block)}")
                return str(content_block)
        else:
            log_message("LLM", "❌ Empty response received")
            return "I apologize, but I received an empty response. Please try again."
            
    except Exception as e:
        log_message("ERROR", f"Error calling Claude 3 Haiku: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later."


class SendMessageRequest(BaseModel):
    message: str
    sender_id: Optional[str] = None  # Optional: to track who sent the message
    partner: Optional[str] = None  # "A" or "B" to identify which partner is speaking


async def store_conversation_async(couple_agent: str, user_message: str, ai_response: str, partner: Optional[str] = None):
    """Async function to store conversation in memory"""
    try:
        # Create enhanced message content with partner info
        partner_prefix = f"[Partner {partner}] " if partner else ""
        enhanced_message = f"{partner_prefix}{user_message}"
        
        # Store both messages in memory
        client.add([
            {"role": "user", "content": enhanced_message},
            {"role": "assistant", "content": ai_response}
        ], user_id=couple_agent)
        
        log_message("ASYNC", f"✅ Conversation stored successfully (Partner: {partner})")
    except Exception as e:
        log_message("ERROR", f"Failed to store conversation asynchronously: {e}")


@router.post("")
async def send_message(couple_id: int, request: SendMessageRequest, background_tasks: BackgroundTasks):
    log_message("INFO", f"=== NEW MESSAGE REQUEST ===")
    log_message("INFO", f"Couple ID: {couple_id}")
    log_message("INFO", f"Message: {request.message[:100]}{'...' if len(request.message) > 100 else ''}")
    log_message("INFO", f"Sender ID: {request.sender_id}")
    log_message("INFO", f"Partner: {request.partner}")
    
    couple_agent = get_couple_ai_agent(couple_id)
    log_message("INFO", f"Couple Agent: {couple_agent}")

    # Search for relevant memories FIRST (before storing new message)
    log_message("INFO", "Searching for relevant memories...")
    memories = client.search(request.message, user_id=couple_agent)
    log_message("INFO", f"✅ Found {len(memories)} relevant memories")
    
    # Log memory details if any found
    if memories:
        for i, memory in enumerate(memories[:3]):  # Show first 3 memories
            if isinstance(memory, dict) and 'memory' in memory:
                log_message("MEMORY", f"Memory {i+1}: {memory['memory'][:80]}{'...' if len(memory['memory']) > 80 else ''}")

    # Construct prompt with partner context
    log_message("INFO", "Constructing AI prompt...")
    prompt_data = construct_prompt(request.message, memories, request.partner)
    log_message("INFO", f"✅ Prompt constructed ({len(prompt_data)} characters)")

    # Call LLM (this is the main latency bottleneck)
    log_message("INFO", "Calling Claude 3 Haiku...")
    ai_response = call_llm(prompt_data)
    log_message("INFO", f"✅ AI response received ({len(ai_response)} characters)")

    # Add storage task to background (truly async)
    log_message("INFO", "Adding storage task to background...")
    background_tasks.add_task(
        store_conversation_async, 
        couple_agent, 
        request.message, 
        ai_response, 
        request.partner
    )
    
    log_message("INFO", "=== REQUEST COMPLETED (storage in background) ===\n")

    return JSONResponse({
        "couple_agent": couple_agent,
        "user_message": request.message,
        "sender_id": request.sender_id,
        "partner": request.partner,
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
