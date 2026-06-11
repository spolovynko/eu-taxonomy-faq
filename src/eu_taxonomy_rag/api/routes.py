from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from eu_taxonomy_rag.agent.factory import agent_factory
from eu_taxonomy_rag.agent.generation import RagAnswer
from eu_taxonomy_rag.agent.rag_agent import RAGAgent

router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        question = value.strip()

        if not question:
            raise ValueError("question cannot be empty")

        return question


@router.post("/chat", response_model=RagAnswer)
def chat(
    request: ChatRequest,
    agent: RAGAgent = Depends(agent_factory.create),
) -> RagAnswer:
    return agent.answer(request.question)


@router.post("/chat/stream")
def stream_chat(
    request: ChatRequest,
    agent: RAGAgent = Depends(agent_factory.create),
) -> StreamingResponse:
    return StreamingResponse(
        agent.stream_answer(request.question),
        media_type="text/plain",
    )
