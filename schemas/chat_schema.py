from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field("default", description="Session ID for conversation memory")
    top_k: Optional[int] = Field(5, ge=1, le=10, description="Number of documents to retrieve")

class ChatResponse(BaseModel):
    query: str
    answer: str
    intent: str
    confidence: float
    sources: List[Dict]
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