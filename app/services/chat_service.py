"""
Chat service — handles RAG: retrieve relevant chunks from FAISS, call LLM, return answer.
Full logic will be implemented in the next phase.
"""


class ChatService:
    async def answer(self, question: str, document_id: str | None = None) -> dict:
        """Retrieve context chunks and generate LLM answer."""
        raise NotImplementedError


chat_service = ChatService()
