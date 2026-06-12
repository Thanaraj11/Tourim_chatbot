from fastapi import APIRouter, HTTPException, Depends
from schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    ClearSessionRequest,
    SessionInfoResponse,
    ToolsListResponse
)
from services.chat_service import ChatService

router = APIRouter()

# Singleton service
_chat_service = None


def get_chat_service() -> ChatService:
    global _chat_service

    if _chat_service is None:
        _chat_service = ChatService()

    return _chat_service


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service)
):
    try:
        result = await service.process_message(
            session_id=request.session_id,
            message=request.message
        )

        return ChatResponse(
            query=result.get("query", request.message),
            answer=result.get("answer", ""),
            intent=result.get("intent", "general"),
            tools_used=result.get("tools_used", []),
            entities=result.get("entities", {}),
            session_id=request.session_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.delete("/session")
async def clear_session(
    request: ClearSessionRequest,
    service: ChatService = Depends(get_chat_service)
):
    try:
        service.clear_session(request.session_id)

        return {
            "status": "success",
            "message": f"Session {request.session_id} cleared"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/session/{session_id}/info",
    response_model=SessionInfoResponse
)
async def get_session_info(
    session_id: str,
    service: ChatService = Depends(get_chat_service)
):
    try:
        info = service.get_session_info(session_id)
        return SessionInfoResponse(**info)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/tools", response_model=ToolsListResponse)
async def list_tools():
    """
    List available tools
    """

    tools = [
        "Weather Tool",
        "Map Tool",
        "Currency Tool",
        "Itinerary Tool",
        "RAG Retrieval"
    ]

    return ToolsListResponse(
        tools=tools,
        count=len(tools)
    )


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "3.0",
        "features": [
            "Tourism Chatbot",
            "Conversation Memory",
            "Weather Tool",
            "Map Tool",
            "Currency Tool",
            "Itinerary Tool",
            "RAG Retrieval"
        ]
    }