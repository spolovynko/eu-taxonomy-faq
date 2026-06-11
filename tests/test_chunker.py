from eu_taxonomy_rag.data_ingestion.chunker import FAQChunker
from eu_taxonomy_rag.data_ingestion.schemas import FAQItem


def test_chunker_splits_long_answer():
    faq = FAQItem(
        faq_id="faq-1",
        section="General",
        question="Question?",
        answer="First paragraph.\n\nSecond paragraph.",
        source_url="https://example.com",
    )

    chunks = FAQChunker(chunk_size=20).chunk([faq])

    assert len(chunks) == 2
    assert chunks[0].chunk_id == "faq-1_chunk_000"
