from typing import Dict, Optional
from memory.chat_memory import MemoryManager
from agents.tourism_agent import TourismAgent
from retrieval.retriever import Retriever
from llm.llm import LLM
from vector_db.vector_db import VectorDB
import os

class ChatService:
    """
    Business logic layer for chat functionality - Version 3 with MySQL memory
    """
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.vector_db = VectorDB()
        self.vector_db.create_collection()
        self.retriever = Retriever(self.vector_db)
        self.llm = LLM(provider=os.getenv("LLM_PROVIDER", "gemini"))
        # No in-memory cache for chains; create new each time (lightweight)
    
    def get_agent(self, session_id: str) -> TourismAgent:
        """Create a tourism agent for a session (memory loaded from MySQL)"""
        memory = self.memory_manager.get_session(session_id)
        return TourismAgent(
            retriever=self.retriever,
            llm=self.llm,
            memory=memory
        )
    
    async def process_message(self, session_id: str, message: str, top_k: int = 5) -> Dict:
        """Process a user message and return response"""
        agent = self.get_agent(session_id)
        result = await agent.process_query(message)
        return result
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        self.memory_manager.clear_session(session_id)
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get information about a session"""
        memory = self.memory_manager.get_session(session_id)
        return {
            "session_id": session_id,
            "message_count": len(memory.get_recent_messages(1000)),  # Get approximate count
            "current_topic": memory.get_current_topic(),
            "context_variables": memory.context_variables
        }