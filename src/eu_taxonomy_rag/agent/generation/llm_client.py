from abc import ABC, abstractmethod
from collections.abc import Iterator

from eu_taxonomy_rag.agent.generation.schemas import RagAnswer
from eu_taxonomy_rag.agent.retrieval.schemas import RetrievedChunk


class LLMClient(ABC):
    @abstractmethod
    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> RagAnswer:
        ...

    @abstractmethod
    def stream(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> Iterator[str]:
        ...
