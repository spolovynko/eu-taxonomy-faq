from collections.abc import Iterator

from eu_taxonomy_rag.agent.generation.llm_client import LLMClient
from eu_taxonomy_rag.agent.generation.schemas import RagAnswer
from eu_taxonomy_rag.agent.retrieval.retriever import Retriever


class RAGAgent:
    def __init__(
        self,
        retriever: Retriever,
        llm_client: LLMClient,
        top_k: int,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        self.retriever = retriever
        self.llm_client = llm_client
        self.top_k = top_k

    def answer(self, question: str) -> RagAnswer:
        question = question.strip()

        if not question:
            raise ValueError("question cannot be empty")

        chunks = self.retriever.retrieve(
            question=question,
            top_k=self.top_k,
        )

        return self.llm_client.generate(
            question=question,
            chunks=chunks,
        )

    def stream_answer(self, question: str) -> Iterator[str]:
        question = question.strip()

        if not question:
            raise ValueError("question cannot be empty")

        chunks = self.retriever.retrieve(
            question=question,
            top_k=self.top_k,
        )

        return self.llm_client.stream(
            question=question,
            chunks=chunks,
        )
