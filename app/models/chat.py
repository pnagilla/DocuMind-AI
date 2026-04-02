from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    document_id: str | None = None  # Optional: scope to a specific document


class SourceChunk(BaseModel):
    content: str
    document_id: str
    page_number: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = []
