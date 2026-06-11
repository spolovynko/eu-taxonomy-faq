from eu_taxonomy_rag.agent.generation.prompt import (
    STREAM_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
)
from eu_taxonomy_rag.agent.retrieval.schemas import RetrievedChunk


class PromptBuilder:
    def build(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> tuple[str, str]:
        question = question.strip()

        if not question:
            raise ValueError("question cannot be empty")

        return SYSTEM_PROMPT, self._build_user_prompt(
            question=question,
            chunks=chunks,
        )

    def build_stream(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> tuple[str, str]:
        question = question.strip()

        if not question:
            raise ValueError("question cannot be empty")

        return STREAM_SYSTEM_PROMPT, self._build_user_prompt(
            question=question,
            chunks=chunks,
        )

    def _build_user_prompt(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> str:
        context = "\n\n".join(
            (
                f"Chunk ID: {chunk.chunk_id}\n"
                f"FAQ question: {chunk.question}\n"
                f"Answer: {chunk.text_for_answering}"
            )
            for chunk in chunks
        )

        if not context:
            context = "No FAQ context was retrieved."

        return (
            f"Context:\n{context}\n\n"
            f"User question: {question}"
        )
