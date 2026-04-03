"""
Document service — handles upload, parsing, chunking, embedding, and FAISS storage.
"""

from typing import Optional, List
import json
import uuid
from pathlib import Path

import faiss
import numpy as np
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class DocumentService:
    def __init__(self):
        self._embedding_model: SentenceTransformer | None = None
        self._index: faiss.Index | None = None
        # Stores chunk metadata: list of {chunk_id, document_id, document_name, content, page_number}
        self._chunks: list[dict] = []
        # Stores document metadata: {document_id: {filename, chunk_count}}
        self._documents: dict[str, dict] = {}
        self._metadata_path = Path(settings.FAISS_INDEX_PATH) / "metadata.json"
        self._index_path = Path(settings.FAISS_INDEX_PATH) / "index.faiss"
        self._load_persisted()

    @property
    def embedding_model(self) -> SentenceTransformer:
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._embedding_model

    def _load_persisted(self):
        """Load existing FAISS index and metadata from disk if available."""
        if self._index_path.exists() and self._metadata_path.exists():
            self._index = faiss.read_index(str(self._index_path))
            with open(self._metadata_path) as f:
                data = json.load(f)
                self._chunks = data.get("chunks", [])
                self._documents = data.get("documents", {})

    def _persist(self):
        """Save FAISS index and metadata to disk."""
        Path(settings.FAISS_INDEX_PATH).mkdir(parents=True, exist_ok=True)
        if self._index is not None:
            faiss.write_index(self._index, str(self._index_path))
        with open(self._metadata_path, "w") as f:
            json.dump({"chunks": self._chunks, "documents": self._documents}, f)

    def _get_or_create_index(self, dim: int) -> faiss.Index:
        if self._index is None:
            self._index = faiss.IndexFlatL2(dim)
        return self._index

    async def process_document(self, file_path: str, document_id: str, filename: str, user_id: str) -> dict:
        """Parse PDF → chunk → embed → store in FAISS."""
        # 1. Parse PDF
        reader = PdfReader(file_path)
        raw_chunks = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                raw_chunks.append({"text": text, "page_number": page_num})

        if not raw_chunks:
            raise ValueError("No extractable text found in the PDF.")

        # 2. Chunk text
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        chunks = []
        for item in raw_chunks:
            pieces = splitter.split_text(item["text"])
            for piece in pieces:
                chunks.append({"text": piece, "page_number": item["page_number"]})

        # 3. Embed
        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True).astype("float32")

        # 4. Store in FAISS
        index = self._get_or_create_index(embeddings.shape[1])
        start_idx = index.ntotal
        index.add(embeddings)

        # 5. Save metadata
        for i, chunk in enumerate(chunks):
            self._chunks.append({
                "faiss_id": start_idx + i,
                "chunk_id": str(uuid.uuid4()),
                "document_id": document_id,
                "document_name": filename,
                "user_id": user_id,
                "content": chunk["text"],
                "page_number": chunk["page_number"],
            })

        self._documents[document_id] = {"filename": filename, "chunk_count": len(chunks), "user_id": user_id}
        self._persist()

        return {"document_id": document_id, "chunk_count": len(chunks)}

    async def list_documents(self, user_id: str) -> List[dict]:
        """Return metadata for all indexed documents belonging to a user."""
        return [
            {"document_id": doc_id, **meta}
            for doc_id, meta in self._documents.items()
            if meta.get("user_id") == user_id
        ]

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Remove a document's chunks from the index and rebuild FAISS."""
        doc = self._documents.get(document_id)
        if not doc or doc.get("user_id") != user_id:
            return False

        # Filter out chunks for this document
        remaining = [c for c in self._chunks if c["document_id"] != document_id]

        # Rebuild FAISS index from remaining chunks
        if remaining:
            texts = [c["content"] for c in remaining]
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True).astype("float32")
            self._index = faiss.IndexFlatL2(embeddings.shape[1])
            self._index.add(embeddings)
            # Re-assign faiss_ids
            for i, chunk in enumerate(remaining):
                chunk["faiss_id"] = i
        else:
            self._index = None

        self._chunks = remaining
        del self._documents[document_id]

        # Remove uploaded PDF file
        upload_file = Path(settings.UPLOAD_DIR) / f"{document_id}.pdf"
        if upload_file.exists():
            upload_file.unlink()

        self._persist()
        return True

    def search(self, query: str, user_id: str, document_id: Optional[str] = None, top_k: Optional[int] = None) -> List[dict]:
        """Retrieve top-K most relevant chunks for a query, filtered by relevance threshold."""
        if self._index is None or self._index.ntotal == 0:
            return []

        k = top_k or settings.MAX_RETRIEVED_CHUNKS
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True).astype("float32")
        distances, indices = self._index.search(query_embedding, min(k * 2, self._index.ntotal))

        # Build a lookup for fast faiss_id → chunk resolution
        faiss_lookup = {c["faiss_id"]: c for c in self._chunks}

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            # Distance threshold — skip chunks that are too dissimilar (L2 distance > 1.5)
            if dist > 1.5:
                continue
            chunk = faiss_lookup.get(int(idx))
            if chunk is None:
                continue
            if chunk.get("user_id") != user_id:
                continue
            if document_id and chunk["document_id"] != document_id:
                continue
            results.append(chunk)
            if len(results) >= k:
                break

        return results


document_service = DocumentService()
