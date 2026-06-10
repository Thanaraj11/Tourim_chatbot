from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router
from vector_db.build_index import build_vector_index
import os

app = FastAPI(title="Tourism Chatbot V1 - RAG System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Tourism Chatbot V1...")
    
    # Check if vector DB exists
    from vector_db.vector_db import VectorDB
    vdb = VectorDB()
    vdb.create_collection()
    
    if vdb.count() == 0:
        print("⚠️ Vector DB is empty. Building index from database...")
        build_vector_index()
    else:
        print(f"✅ Vector DB ready with {vdb.count()} documents")

@app.get("/")
async def root():
    return {
        "name": "Tourism Chatbot V1",
        "version": "1.0",
        "description": "RAG-based tourism assistant",
        "endpoints": {
            "chat": "POST /api/v1/chat",
            "health": "GET /api/v1/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )