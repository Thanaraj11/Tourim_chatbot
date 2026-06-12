from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router
from vector_db.build_index import build_vector_index
import os

app = FastAPI(
    title="Tourism Chatbot V3 - AI Tourism Assistant",
    description="Agent-based tourism assistant with weather, maps, currency, and itinerary tools",
    version="3.0"
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
app.include_router(chat_router, prefix="/api/v3", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    print("Starting Tourism Chatbot V3 (AI Agent)...")
    print("Initializing Agent with tools...")
    
    from vector_db.vector_db import VectorDB
    vdb = VectorDB()
    vdb.create_collection()
    
    if vdb.count() == 0:
        print("Vector DB is empty. Building index from database...")
        build_vector_index()
    else:
        print(f"Vector DB ready with {vdb.count()} documents")
    
    print("\nAI Agent Features Enabled:")
    print("   Agent Decision Making")
    print("   Weather Tool")
    print("   Map Tool")
    print("   Currency Tool")
    print("   Itinerary Tool")
    print("   RAG Retriever")
    print("\nServer running at http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")

@app.get("/")
async def root():
    return {
        "name": "Tourism Chatbot V3",
        "version": "3.0",
        "description": "AI Agent-based tourism assistant with dynamic tool selection",
        "features": [
            "Agent architecture with decision making",
            "Weather information (real-time)",
            "Maps and distance calculation",
            "Currency exchange rates",
            "Travel itinerary planning",
            "Smart tool routing"
        ],
        "endpoints": {
            "chat": "POST /api/v3/chat",
            "session_info": "GET /api/v3/session/{session_id}/info",
            "clear_session": "DELETE /api/v3/session",
            "list_tools": "GET /api/v3/tools",
            "health": "GET /api/v3/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)