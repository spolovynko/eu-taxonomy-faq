import json
from pathlib import Path

from pydantic import TypeAdapter

from eu_taxonomy_rag.agent.retrieval.vector_store import QdrantVectorStore
from eu_taxonomy_rag.config import get_settings
from eu_taxonomy_rag.data_ingestion.chunker import FAQChunker
from eu_taxonomy_rag.data_ingestion.cleaner import FAQCleaner
from eu_taxonomy_rag.data_ingestion.indexer import FAQIndexer
from eu_taxonomy_rag.data_ingestion.openai_embedder import OpenAIEmbedder
from eu_taxonomy_rag.data_ingestion.schemas import Chunk, FAQItem


def load_faqs(path: Path) -> list[FAQItem]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return TypeAdapter(list[FAQItem]).validate_python(data)


def save_chunks(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(chunk.model_dump_json() + "\n")


def main() -> None:
    settings = get_settings()
    faqs = load_faqs(settings.faq_output_path)

    vector_store = QdrantVectorStore(
        url=settings.qdrant_url,
        collection_name=settings.qdrant_collection,
    )
    indexer = FAQIndexer(
        cleaner=FAQCleaner(),
        chunker=FAQChunker(settings.chunk_size),
        embedder=OpenAIEmbedder(
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
            batch_size=settings.embedding_batch_size,
        ),
        vector_store=vector_store,
    )

    cleaned_count, chunks = indexer.index(faqs)
    save_chunks(chunks, settings.chunks_output_path)

    print(f"Loaded FAQs: {len(faqs)}")
    print(f"Cleaned FAQs: {cleaned_count}")
    print(f"Created chunks: {len(chunks)}")
    print(f"Indexed chunks: {vector_store.count()}")
    print(f"Saved chunks to: {settings.chunks_output_path}")


if __name__ == "__main__":
    main()
