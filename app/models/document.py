from pydantic import BaseModel
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
    uploaded_at: datetime


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    page_number: int | None = None
    metadata: dict = {}
