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

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))



def log_message(level: str, message: str):
    """Helper function to log messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def get_couple_ai_agent(couple_id: int) -> str:
    return f"couple_{couple_id}"


def get_partner_agent(couple_id: int, partner: str) -> str:
    """Get agent ID for a specific partner within a couple"""
    return f"couple_{couple_id}_{partner}"


def get_couple_agent(couple_id: int) -> str:
    """Get the main couple agent for shared memories"""
    return f"couple_{couple_id}_shared"


def construct_prompt(message: str, memories: List[Dict[str, Any]], partner: Optional[str] = None, couple_names: Optional[Dict[str, str]] = None):

    # Get partner names or use defaults
    partner_a_name = couple_names.get("A", "Partner A") if couple_names else "Partner A"
    partner_b_name = couple_names.get("B", "Partner B") if couple_names else "Partner B"
    current_speaker = couple_names.get(partner, f"Partner {partner}") if couple_names and partner else f"Partner {partner}" if partner else "User"

    system_prompt = f"""You are an AI couples therapy assistant of {partner_a_name} and {partner_b_name}.
Your role:
- Prioritize listening and emotional validation before giving advice.
- Reflect the user's feelings and intentions, then gently offer perspective if needed.
- Use prior conversation history (specific to the current partner) to remember relationship dynamics.
- Be warm, supportive, and non-judgmental.
- Let the user lead; suggest only after emotional cues are heard and acknowledged.
- Avoid repeating your identity or stating your role in responses.
- When a user shares pride, joy, or success, **stay with that emotion first** — celebrate and explore before shifting to relationship matters (unless they initiate).
- Avoid therapist jargon. Use natural, compassionate, human-like language.
- Keep {partner_a_name} and {partner_b_name}'s context separate — never mix memories or cross-address.
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
    if partner and couple_names:
        partner_context = f"\nCurrent Speaker: {current_speaker}"
        system_prompt += f"\n\nNote: The current message is from {current_speaker}. Consider their perspective and any patterns in their communication style from previous conversations."

    # Extract memory context
    memory_context = []
    for memory in memories:
        if isinstance(memory, dict) and 'memory' in memory:
            memory_context.append(memory['memory'])

    rag_context = "\n".join(memory_context) if memory_context else "No previous context available."

    full_prompt = f"""System: {system_prompt}

Context from Past Conversations:
{rag_context}

{partner_context}

New Message from {current_speaker}:
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
    couple_names: Optional[Dict[str, str]] = None  # {"A": "Alex", "B": "Mary"} or similar


async def store_conversation_async(couple_agent: str, partner_agent: Optional[str], user_message: str, ai_response: str, partner: Optional[str] = None, couple_names: Optional[Dict[str, str]] = None):
    """Async function to store conversation in memory using agents"""
    try:
        # Create enhanced message content with partner name and context
        if couple_names and partner:
            partner_name = couple_names.get(partner, f"Partner {partner}")
            enhanced_message = f"{partner_name}: {user_message}"
        else:
            partner_prefix = f"Partner {partner}: " if partner else ""
            enhanced_message = f"{partner_prefix}{user_message}"
        
        # Store only the user message in couple's shared memory space (no AI response)
        log_message("ASYNC", f"Storing user message in couple's shared memory: {couple_agent}")
        client.add([
            {"role": "user", "content": enhanced_message}
        ], agent_id=couple_agent)
        
        # Also store only the user message in partner's individual memory space if available
        if partner_agent:
            log_message("ASYNC", f"Storing user message in partner's individual memory: {partner_agent}")
            client.add([
                {"role": "user", "content": enhanced_message}
            ], agent_id=partner_agent)
        
        log_message("ASYNC", f"✅ User message stored successfully (Speaker: {partner})")
    except Exception as e:
        log_message("ERROR", f"Failed to store conversation asynchronously: {e}")


@router.post("")
async def send_message(couple_id: int, request: SendMessageRequest, background_tasks: BackgroundTasks):
    log_message("INFO", f"=== NEW MESSAGE REQUEST ===")
    log_message("INFO", f"Couple ID: {couple_id}")
    log_message("INFO", f"Message: {request.message[:100]}{'...' if len(request.message) > 100 else ''}")
    log_message("INFO", f"Sender ID: {request.sender_id}")
    log_message("INFO", f"Partner: {request.partner}")
    log_message("INFO", f"Couple Names: {request.couple_names}")
    
    # Get agent IDs
    couple_agent = get_couple_agent(couple_id)
    partner_agent = get_partner_agent(couple_id, request.partner) if request.partner else None
    
    log_message("INFO", f"Couple Agent: {couple_agent}")
    log_message("INFO", f"Partner Agent: {partner_agent}")

    # Search for relevant memories from both couple and partner agents
    log_message("INFO", "Searching for relevant memories...")
    
    # Search in couple's shared memories
    couple_memories = client.search(request.message, agent_id=couple_agent)
    log_message("INFO", f"✅ Found {len(couple_memories)} memories in couple's shared space")
    
    # Search in partner's individual memories
    partner_memories = []
    if partner_agent:
        partner_memories = client.search(request.message, agent_id=partner_agent)
        log_message("INFO", f"✅ Found {len(partner_memories)} memories in partner's individual space")
    
    # Combine memories (couple memories first, then partner memories)
    all_memories = couple_memories + partner_memories
    log_message("INFO", f"✅ Total memories found: {len(all_memories)}")
    
    # Log memory details if any found
    if all_memories:
        for i, memory in enumerate(all_memories[:3]):  # Show first 3 memories
            if isinstance(memory, dict) and 'memory' in memory:
                log_message("MEMORY", f"Memory {i+1}: {memory['memory'][:80]}{'...' if len(memory['memory']) > 80 else ''}")

    # Construct prompt with partner context
    log_message("INFO", "Constructing AI prompt...")
    prompt_data = construct_prompt(request.message, all_memories, request.partner, request.couple_names)
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
        partner_agent,
        request.message, 
        ai_response, 
        request.partner,
        request.couple_names
    )
    
    log_message("INFO", "=== REQUEST COMPLETED (storage in background) ===\n")

    return JSONResponse({
        "couple_agent": couple_agent,
        "partner_agent": partner_agent,
        "user_message": request.message,
        "sender_id": request.sender_id,
        "partner": request.partner,
        "couple_names": request.couple_names,
        "ai_response": ai_response,
        "prompt_data": prompt_data,
        "memories_used": len(all_memories),
        "couple_memories": len(couple_memories),
        "partner_memories": len(partner_memories)
    })


@router.get("")
async def get_messages(couple_id: int):
    # TODO: Implement message retrieval logic
    return JSONResponse([
        {"id": 1, "sender": "user1@example.com", "text": "Hello!", "timestamp": "2024-01-01T00:00:00Z"},
        {"id": 2, "sender": "user2@example.com", "text": "Hi!", "timestamp": "2024-01-01T00:01:00Z"}
    ])
