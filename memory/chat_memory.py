from typing import List, Dict, Optional
from datetime import datetime
import json
import os

class ChatMemory:
    def __init__(self, session_id: str = "default", max_history: int = 20):
        self.session_id = session_id
        self.max_history = max_history
        self.conversation_history: List[Dict] = []
        self.context_variables: Dict = {}
        
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history"""
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        
        # Trim if exceeds max
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_recent_messages(self, count: int = 5) -> List[Dict]:
        """Get last N messages"""
        return self.conversation_history[-count:]
    
    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation for context"""
        if not self.conversation_history:
            return ""
        
        summary_parts = []
        for msg in self.conversation_history[-6:]:  # Last 3 exchanges
            role = "User" if msg["role"] == "user" else "Assistant"
            summary_parts.append(f"{role}: {msg['content'][:100]}")
        
        return "\n".join(summary_parts)
    
    def get_last_user_query(self) -> Optional[str]:
        """Get the most recent user query"""
        for msg in reversed(self.conversation_history):
            if msg["role"] == "user":
                return msg["content"]
        return None
    
    def get_last_assistant_response(self) -> Optional[str]:
        """Get the most recent assistant response"""
        for msg in reversed(self.conversation_history):
            if msg["role"] == "assistant":
                return msg["content"]
        return None
    
    def get_current_topic(self) -> Optional[str]:
        """Infer current topic from conversation"""
        # Look for mentioned places/entities in recent messages
        places_keywords = ["sigiriya", "kandy", "ella", "galle", "colombo", "hotel", "restaurant"]
        recent = self.get_recent_messages(4)
        
        for msg in recent:
            msg_lower = msg["content"].lower()
            for keyword in places_keywords:
                if keyword in msg_lower:
                    return keyword.title()
        return None
    
    def update_context(self, key: str, value: any):
        """Store context variables (e.g., current place being discussed)"""
        self.context_variables[key] = value
    
    def get_context(self, key: str) -> any:
        """Retrieve context variable"""
        return self.context_variables.get(key)
    
    def clear(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.context_variables = {}
    
    def save_to_file(self, filepath: str):
        """Persist memory to file"""
        data = {
            "session_id": self.session_id,
            "history": self.conversation_history,
            "context": self.context_variables
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load memory from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.conversation_history = data.get("history", [])
                self.context_variables = data.get("context", {})

class MemoryManager:
    """Manages multiple chat sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatMemory] = {}
    
    def get_session(self, session_id: str) -> ChatMemory:
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatMemory(session_id)
        return self.sessions[session_id]
    
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id].clear()