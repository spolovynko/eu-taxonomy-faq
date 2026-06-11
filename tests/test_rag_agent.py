from eu_taxonomy_rag.agent.generation.schemas import RagAnswer
from eu_taxonomy_rag.agent.rag_agent import RAGAgent


class FakeRetriever:
    def retrieve(self, question, top_k):
        self.call = (question, top_k)
        return []


class FakeLLMClient:
    def generate(self, question, chunks):
        return RagAnswer(
            answer="Test answer",
            confidence="high",
            used_chunk_ids=[],
            insufficient_context=False,
        )


def test_agent_uses_configured_top_k():
    retriever = FakeRetriever()
    agent = RAGAgent(retriever, FakeLLMClient(), top_k=3)

    answer = agent.answer("Question")

    assert retriever.call == ("Question", 3)
    assert answer.answer == "Test answer"
