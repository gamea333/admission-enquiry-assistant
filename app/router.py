import uuid

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.rag.generator import generate_answer
from app.schemas import ChatRequest, ChatResponse, HealthResponse, SourceDocument

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", app_name=settings.app_name)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    settings = get_settings()
    if not settings.google_api_key:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_API_KEY is not configured. Set it in your .env file.",
        )

    try:
        answer, docs = generate_answer(request.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    sources = [
        SourceDocument(
            content=doc.page_content[:500],
            source=doc.metadata.get("source"),
            page=doc.metadata.get("page"),
        )
        for doc in docs
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
        session_id=request.session_id or str(uuid.uuid4()),
    )
