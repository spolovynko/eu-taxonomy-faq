from eu_taxonomy_rag.agent.retrieval.vector_store import QdrantVectorStore
from eu_taxonomy_rag.data_ingestion.chunker import FAQChunker
from eu_taxonomy_rag.data_ingestion.cleaner import FAQCleaner
from eu_taxonomy_rag.data_ingestion.embedder import Embedder
from eu_taxonomy_rag.data_ingestion.schemas import Chunk, FAQItem


class FAQIndexer:
    def __init__(
        self,
        cleaner: FAQCleaner,
        chunker: FAQChunker,
        embedder: Embedder,
        vector_store: QdrantVectorStore,
    ) -> None:
        self.cleaner = cleaner
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    def index(self, faqs: list[FAQItem]) -> tuple[int, list[Chunk]]:
        cleaned_faqs = self.cleaner.clean(faqs)
        chunks = self.chunker.chunk(cleaned_faqs)

        if not chunks:
            raise RuntimeError("No chunks were created from the FAQ data")

        vectors = self.embedder.embed_documents(
            [chunk.text_for_embedding for chunk in chunks]
        )

        if not vectors:
            raise RuntimeError("No embedding vectors were created")

        vector_size = len(vectors[0])

        if any(len(vector) != vector_size for vector in vectors):
            raise RuntimeError("Embedding vectors have inconsistent sizes")

        self.vector_store.recreate_collection(vector_size)
        self.vector_store.upsert_chunks(chunks, vectors)

        indexed_count = self.vector_store.count()

        if indexed_count != len(chunks):
            raise RuntimeError(
                f"Expected {len(chunks)} indexed chunks, found {indexed_count}"
            )

        return len(cleaned_faqs), chunks
