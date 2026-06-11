from fastapi.testclient import TestClient

from eu_taxonomy_rag.agent.factory import agent_factory
from eu_taxonomy_rag.agent.generation.schemas import RagAnswer
from eu_taxonomy_rag.agent.rag_agent import RAGAgent
from eu_taxonomy_rag.agent.retrieval.schemas import RetrievedChunk
from eu_taxonomy_rag.main import app


class FakeRetriever:
    def retrieve(self, question, top_k):
        return [
            RetrievedChunk(
                chunk_id="chunk-1",
                faq_id="faq-1",
                section="General",
                question="What is the EU Taxonomy?",
                text_for_answering="It is a classification system.",
                source_url="https://example.com/faq",
                score=0.9,
            )
        ]


class FakeLLMClient:
    def generate(self, question, chunks):
        return RagAnswer(
            answer=chunks[0].text_for_answering,
            confidence="high",
            used_chunk_ids=[chunks[0].chunk_id],
            insufficient_context=False,
        )


def test_chat_smoke_flow():
    agent = RAGAgent(FakeRetriever(), FakeLLMClient(), top_k=1)
    app.dependency_overrides[agent_factory.create] = lambda: agent

    try:
        response = TestClient(app).post(
            "/api/chat",
            json={"question": "What is the EU Taxonomy?"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "answer": "It is a classification system.",
        "confidence": "high",
        "used_chunk_ids": ["chunk-1"],
        "insufficient_context": False,
    }
