"""
Gemini AI Agent for legal consultations
"""
import google.generativeai as genai
from typing import Dict, Optional
import uuid

class GeminiAgent:
    def __init__(self, api_key: str):
        """Initialize Gemini agent"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.conversations = {}
        
    async def chat(self, message: str, conversation_id: Optional[str] = None) -> Dict:
        """
        Chat with Gemini AI agent
        """
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            self.conversations[conversation_id] = []
        
        system_prompt = """Tu esi Lietuvos teisės ekspertas ir AI asistentas. 
        Tavo užduotis - padėti vartotojams suprasti Lietuvos teisės aktus."""
        
        if conversation_id in self.conversations:
            context = "\n".join(self.conversations[conversation_id])
            full_message = f"{system_prompt}\n\nKontekstas:\n{context}\n\nKlausimas: {message}"
        else:
            full_message = f"{system_prompt}\n\nKlausimas: {message}"
        
        response = self.model.generate_content(full_message)
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        self.conversations[conversation_id].append(f"User: {message}")
        self.conversations[conversation_id].append(f"AI: {response.text}")
        
        return {
            "message": response.text,
            "conversation_id": conversation_id
        }
