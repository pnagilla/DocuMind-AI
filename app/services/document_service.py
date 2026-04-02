"""
Document service — handles upload, parsing, chunking, embedding, and FAISS storage.
Full logic will be implemented in the next phase.
"""


class DocumentService:
    async def process_document(self, file_path: str, document_id: str) -> dict:
        """Parse PDF → chunk → embed → store in FAISS."""
        raise NotImplementedError

    async def list_documents(self) -> list[dict]:
        """Return metadata for all indexed documents."""
        raise NotImplementedError

    async def delete_document(self, document_id: str) -> bool:
        """Remove a document and its vectors from the index."""
        raise NotImplementedError


document_service = DocumentService()
