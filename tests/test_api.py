from fastapi.testclient import TestClient

from eu_taxonomy_rag.agent.factory import agent_factory
from eu_taxonomy_rag.agent.generation.schemas import RagAnswer
from eu_taxonomy_rag.main import app


class FakeAgent:
    def answer(self, question):
        return RagAnswer(
            answer=f"Answer to {question}",
            confidence="high",
            used_chunk_ids=[],
            insufficient_context=False,
        )


def test_chat_endpoint_returns_answer():
    app.dependency_overrides[agent_factory.create] = lambda: FakeAgent()

    response = TestClient(app).post(
        "/api/chat",
        json={"question": "What is the EU Taxonomy?"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["answer"] == "Answer to What is the EU Taxonomy?"
