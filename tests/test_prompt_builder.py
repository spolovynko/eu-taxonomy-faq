from eu_taxonomy_rag.agent.generation.prompt_builder import PromptBuilder
from eu_taxonomy_rag.agent.retrieval.schemas import RetrievedChunk


def test_prompt_contains_question_and_context():
    chunk = RetrievedChunk(
        chunk_id="chunk-1",
        faq_id="faq-1",
        section="General",
        question="What is the Taxonomy?",
        text_for_answering="It is a classification system.",
        source_url="https://example.com",
        score=0.9,
    )

    _, user_prompt = PromptBuilder().build("Explain it", [chunk])

    assert "It is a classification system." in user_prompt
    assert "User question: Explain it" in user_prompt
