from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field("default", description="Session ID for conversation memory")

class ChatResponse(BaseModel):
    query: str
    answer: str
    intent: str
    tools_used: List[str] = []
    entities: Optional[Dict] = {}
    session_id: Optional[str] = "default"
    timestamp: datetime = Field(default_factory=datetime.now)

class ClearSessionRequest(BaseModel):
    session_id: str

class SessionInfoResponse(BaseModel):
    session_id: str
    message_count: int
    current_topic: Optional[str]
    context_variables: Dict
    available_tools: List[Dict] = []

class ToolsListResponse(BaseModel):
    tools: List[Dict]
    count: int