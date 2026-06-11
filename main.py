from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router
from vector_db.build_index import build_vector_index
import os

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Tourism Chatbot V2 (Advanced RAG)...")
    
    from vector_db.vector_db import VectorDB
    vdb = VectorDB()
    vdb.create_collection()
    
    if vdb.count() == 0:
        print("⚠️ Vector DB is empty. Building index from database...")
        build_vector_index()
    else:
        print(f"✅ Vector DB ready with {vdb.count()} documents")
    
    print("✅ Features enabled:")
    print("   - Conversation Memory")
    print("   - Query Classification")
    print("   - Metadata Filtering")
    print("   - Document Reranking")
    print("   - Session Management")
    yield

app = FastAPI(
    title="Tourism Chatbot V2 - Advanced RAG System",
    description="Context-aware tourism assistant with memory, intent classification, and smart retrieval",
    version="2.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v2", tags=["chat"])

@app.get("/")
async def root():
    return {
        "name": "Tourism Chatbot V2",
        "version": "2.0",
        "description": "Advanced RAG-based tourism assistant with memory and context awareness",
        "features": [
            "Conversation memory",
            "Intent classification", 
            "Metadata filtering",
            "Document reranking",
            "Session management"
        ],
        "endpoints": {
            "chat": "POST /api/v2/chat",
            "session_info": "GET /api/v2/session/{session_id}/info",
            "clear_session": "DELETE /api/v2/session",
            "health": "GET /api/v2/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)