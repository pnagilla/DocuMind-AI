import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.core.config import settings
from app.models.document import DocumentUploadResponse
from app.routes.auth import get_current_user
from app.services.document_service import document_service

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
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

    await document_service.process_document(
        str(upload_path), document_id, file.filename, current_user["user_id"]
    )

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status="processed",
        message="Document uploaded and indexed successfully.",
        uploaded_at=datetime.now(timezone.utc),
    )


@router.get("/", summary="List all documents")
async def list_documents(current_user: dict = Depends(get_current_user)):
    """Return a list of all indexed documents for the current user."""
    docs = await document_service.list_documents(current_user["user_id"])
    return {"documents": docs}


@router.delete("/{document_id}", summary="Delete a document")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Remove a document from the index."""
    deleted = await document_service.delete_document(document_id, current_user["user_id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found.",
        )
    return {"deleted": document_id}
