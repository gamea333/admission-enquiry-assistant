from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User enquiry message")
    session_id: str | None = Field(None, description="Optional session identifier")


class SourceDocument(BaseModel):
    content: str
    source: str | None = None
    page: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDocument] = []
    session_id: str | None = None


class HealthResponse(BaseModel):
    status: str
    app_name: str
