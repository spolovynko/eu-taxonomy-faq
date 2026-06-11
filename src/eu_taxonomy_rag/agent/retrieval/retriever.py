from eu_taxonomy_rag.agent.retrieval.schemas import RetrievedChunk
from eu_taxonomy_rag.agent.retrieval.vector_store import QdrantVectorStore
from eu_taxonomy_rag.data_ingestion.embedder import Embedder


class Retriever:
    def __init__(
        self,
        embedder: Embedder,
        vector_store: QdrantVectorStore,
    ) -> None:
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(
        self,
        question: str,
        top_k: int,
    ) -> list[RetrievedChunk]:
        question = question.strip()

        if not question:
            raise ValueError("question cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        query_vector = self.embedder.embed_query(question)

        return self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
        )