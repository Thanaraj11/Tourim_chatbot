from typing import Dict, Optional
from memory.chat_memory import MemoryManager
from chains.tourism_chain import TourismChain
from retrieval.retriever import Retriever
from llm.llm import LLM
from vector_db.vector_db import VectorDB
import os

class ChatService:
    """
    Business logic layer for chat functionality
    """
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.vector_db = VectorDB()
        self.vector_db.create_collection()
        self.retriever = Retriever(self.vector_db)
        self.llm = LLM(provider=os.getenv("LLM_PROVIDER", "gemini"))
        self.chains = {}  # Cache chains by session_id
    
    def get_chain(self, session_id: str) -> TourismChain:
        """Get or create a tourism chain for a session"""
        if session_id not in self.chains:
            memory = self.memory_manager.get_session(session_id)
            self.chains[session_id] = TourismChain(
                retriever=self.retriever,
                llm=self.llm,
                memory=memory
            )
        return self.chains[session_id]
    
    async def process_message(self, session_id: str, message: str, top_k: int = 5) -> Dict:
        """
        Process a user message and return response
        """
        chain = self.get_chain(session_id)
        
        # Temporarily override top_k if needed
        # (can be extended to pass to chain)
        try:
           result = chain.run(message)
        except Exception as e:
           raise Exception(f"Chain execution failed: {str(e)}")
        
        return result
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.chains:
            del self.chains[session_id]
        self.memory_manager.clear_session(session_id)
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get information about a session"""
        memory = self.memory_manager.get_session(session_id)
        return {
            "session_id": session_id,
            "message_count": len(memory.conversation_history),
            "current_topic": memory.get_current_topic(),
            "context_variables": memory.context_variables
        }