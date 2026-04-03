from fastapi import APIRouter, Depends, HTTPException, status

from app.models.chat import ChatRequest, ChatResponse, SourceChunk
from app.routes.auth import get_current_user
from app.services.chat_service import chat_service

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Ask a question. Returns an LLM-generated answer grounded in uploaded documents."""
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    response = await chat_service.answer(
        request.question,
        user_id=current_user["user_id"],
        document_id=request.document_id,
    )
    return ChatResponse(
        answer=response["answer"],
        sources=[SourceChunk(**s) for s in response["sources"]],
    )
