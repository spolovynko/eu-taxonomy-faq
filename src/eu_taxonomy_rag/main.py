from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from eu_taxonomy_rag.agent.factory import agent_factory
from eu_taxonomy_rag.agent.generation import RagAnswer
from eu_taxonomy_rag.agent.rag_agent import RAGAgent
from eu_taxonomy_rag.config import get_settings

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="EU Taxonomy FAQ")


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        question = value.strip()

        if not question:
            raise ValueError("question cannot be empty")

        return question


@app.post("/api/chat", response_model=RagAnswer)
def chat(
    request: ChatRequest,
    agent: RAGAgent = Depends(agent_factory.create),
) -> RagAnswer:
    return agent.answer(request.question)


@app.post("/api/chat/stream")
def stream_chat(
    request: ChatRequest,
    agent: RAGAgent = Depends(agent_factory.create),
) -> StreamingResponse:
    return StreamingResponse(
        agent.stream_answer(request.question),
        media_type="text/plain",
    )


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


def run():
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
