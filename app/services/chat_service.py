"""
Chat service — handles RAG: retrieve relevant chunks from FAISS, call LLM, return answer.
"""

from typing import Optional
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.document_service import document_service


SYSTEM_PROMPT = """You are DocuMind AI, a helpful assistant that answers questions strictly based on the provided document context.
If the answer cannot be found in the context, say so honestly — do not make up information.
Always be concise and accurate."""


class ChatService:
    def __init__(self):
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
        return self._client

    async def answer(self, question: str, user_id: str, document_id: Optional[str] = None) -> dict:
        """Retrieve context chunks and generate LLM answer."""
        chunks = document_service.search(question, user_id=user_id, document_id=document_id)

        if not chunks:
            return {
                "answer": "No relevant documents found. Please upload a PDF document first.",
                "sources": [],
            }

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(chunks, start=1):
            context_parts.append(
                f"[Source {i} — {chunk['document_name']}, page {chunk['page_number']}]\n{chunk['content']}"
            )
        context = "\n\n".join(context_parts)

        user_message = f"Context:\n{context}\n\nQuestion: {question}"

        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
        )

        answer_text = response.choices[0].message.content.strip()

        sources = [
            {
                "content": chunk["content"],
                "document_id": chunk["document_id"],
                "document_name": chunk.get("document_name", "Unknown"),
                "page_number": chunk["page_number"],
            }
            for chunk in chunks
        ]

        return {"answer": answer_text, "sources": sources}


chat_service = ChatService()
