from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from rag.rag_service import RAGService
from retrieval.retriever import Retriever
from llm.llm import LLM
from vector_db.vector_db import VectorDB
import os

router = APIRouter()

# Global service instances (initialized in main.py)
rag_service = None

def init_rag_service():
    global rag_service
    if rag_service is None:
        vector_db = VectorDB()
        vector_db.create_collection()
        retriever = Retriever(vector_db)
        llm = LLM(provider=os.getenv("LLM_PROVIDER", "gemini"))
        rag_service = RAGService(retriever, llm)
    return rag_service

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        service = init_rag_service()
        result = service.answer_question(request.message, request.top_k)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0"}