from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.rag.generator import answer_query
from app.schemas import ChatRequest, ChatResponse, HealthResponse

router = APIRouter()

NO_CONTEXT_ANSWER = (
    "I don't have that information in our records. "
    "Please contact the admissions office at +91 80 4123 5600 or admissions@greenfield.edu.in."
)


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
        result = answer_query(request.query)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Document index not found. Run `python -m app.rag.ingest` first.",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {exc}") from exc

    answer = result.get("answer", "").strip()
    sources = result.get("sources", [])

    if not answer and not sources:
        return ChatResponse(answer=NO_CONTEXT_ANSWER, sources=[])

    return ChatResponse(answer=answer, sources=sources)
