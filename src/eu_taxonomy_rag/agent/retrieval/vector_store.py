from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient, models

from eu_taxonomy_rag.agent.retrieval.schemas import RetrievedChunk
from eu_taxonomy_rag.data_ingestion.schemas import Chunk


class QdrantVectorStore:
    def __init__(
        self,
        url: str,
        collection_name: str,
    ) -> None:
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name

    def recreate_collection(self, vector_size: int) -> None:
        if vector_size <= 0:
            raise ValueError("vector_size must be greater than zero")

        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    def upsert_chunks(
        self,
        chunks: list[Chunk],
        vectors: list[list[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("Each chunk must have one embedding vector")

        points = [
            models.PointStruct(
                id=str(uuid5(NAMESPACE_URL, chunk.chunk_id)),
                vector=vector,
                payload={
                    "chunk_id": chunk.chunk_id,
                    "faq_id": chunk.faq_id,
                    "section": chunk.section,
                    "question": chunk.question,
                    "text_for_answering": chunk.text_for_answering,
                    "source_url": chunk.source_url,
                },
            )
            for chunk, vector in zip(chunks, vectors)
        ]

        if not points:
            return

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

    def search(
        self,
        query_vector: list[float],
        top_k: int,
    ) -> list[RetrievedChunk]:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        results: list[RetrievedChunk] = []

        for point in response.points:
            payload = point.payload or {}

            results.append(
                RetrievedChunk(
                    chunk_id=payload["chunk_id"],
                    faq_id=payload["faq_id"],
                    section=payload["section"],
                    question=payload["question"],
                    text_for_answering=payload["text_for_answering"],
                    source_url=payload["source_url"],
                    score=point.score,
                )
            )

        return results

    def count(self) -> int:
        result = self.client.count(
            collection_name=self.collection_name,
            exact=True,
        )

        return result.count