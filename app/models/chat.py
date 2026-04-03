from typing import Optional, List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    document_id: Optional[str] = None  # Optional: scope to a specific document


class SourceChunk(BaseModel):
    content: str
    document_id: str
    document_name: Optional[str] = None
    page_number: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = []
