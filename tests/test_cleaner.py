from eu_taxonomy_rag.data_ingestion.cleaner import FAQCleaner
from eu_taxonomy_rag.data_ingestion.schemas import FAQItem


def test_cleaner_normalizes_whitespace():
    faq = FAQItem(
        faq_id=" faq-1 ",
        section=" EU   Taxonomy ",
        question=" What   is it? ",
        answer=" A   classification\n\nsystem. ",
        source_url=" https://example.com ",
    )

    cleaned = FAQCleaner().clean([faq])[0]

    assert cleaned.question == "What is it?"
    assert cleaned.answer == "A classification\n\nsystem."
