"""
Chat API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agents.gemini_agent import GeminiAgent
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    
@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to AI"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        agent = GeminiAgent(api_key)
        response = await agent.chat(request.message, request.conversation_id)
        
        return ChatResponse(
            response=response["message"],
            conversation_id=response["conversation_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
