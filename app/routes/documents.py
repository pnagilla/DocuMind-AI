import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.core.config import settings
from app.models.document import DocumentUploadResponse

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document for processing."""
    suffix = Path(file.filename).suffix.lower()
    if suffix not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {settings.ALLOWED_EXTENSIONS} files are supported.",
        )

    document_id = str(uuid.uuid4())
    upload_path = Path(settings.UPLOAD_DIR) / f"{document_id}{suffix}"
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit.",
        )

    upload_path.write_bytes(content)

    # TODO: trigger document_service.process_document(str(upload_path), document_id)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status="queued",
        message="Document uploaded. Processing will begin shortly.",
        uploaded_at=datetime.now(timezone.utc),
    )


@router.get("/", summary="List all documents")
async def list_documents():
    """Return a list of all indexed documents."""
    # TODO: return document_service.list_documents()
    return {"documents": []}


@router.delete("/{document_id}", summary="Delete a document")
async def delete_document(document_id: str):
    """Remove a document from the index."""
    # TODO: document_service.delete_document(document_id)
    return {"deleted": document_id}
