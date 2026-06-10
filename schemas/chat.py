from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    top_k: Optional[int] = 5

class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[dict]
    confidence: float