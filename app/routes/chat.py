from fastapi import APIRouter, HTTPException, status

from app.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Ask a question. Returns an LLM-generated answer grounded in uploaded documents."""
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    # TODO: response = await chat_service.answer(request.question, request.document_id)
    return ChatResponse(
        answer="Chat logic not yet implemented.",
        sources=[],
    )
