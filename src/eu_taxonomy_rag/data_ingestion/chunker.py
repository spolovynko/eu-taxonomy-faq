from eu_taxonomy_rag.data_ingestion.schemas import Chunk, FAQItem


class FAQChunker:
    def __init__(self, chunk_size: int) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        self.chunk_size = chunk_size

    def chunk(self, faqs: list[FAQItem]) -> list[Chunk]:
        chunks: list[Chunk] = []

        for faq in faqs:
            for index, answer in enumerate(self._split_answer(faq.answer)):
                chunks.append(
                    Chunk(
                        chunk_id=f"{faq.faq_id}_chunk_{index:03d}",
                        faq_id=faq.faq_id,
                        section=faq.section,
                        question=faq.question,
                        text_for_embedding=(
                            f"Question: {faq.question}\n\n"
                            f"Answer: {answer}"
                        ),
                        text_for_answering=answer,
                        source_url=faq.source_url,
                    )
                )

        return chunks

    def _split_answer(self, answer: str) -> list[str]:
        if len(answer) <= self.chunk_size:
            return [answer]

        paragraphs = [
            paragraph.strip()
            for paragraph in answer.split("\n\n")
            if paragraph.strip()
        ]

        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            if len(paragraph) > self.chunk_size:
                if current:
                    chunks.append(current)
                    current = ""

                chunks.extend(self._split_large_paragraph(paragraph))
                continue

            candidate = (
                f"{current}\n\n{paragraph}"
                if current
                else paragraph
            )

            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                chunks.append(current)
                current = paragraph

        if current:
            chunks.append(current)

        return chunks

    def _split_large_paragraph(self, paragraph: str) -> list[str]:
        return [
            paragraph[start : start + self.chunk_size].strip()
            for start in range(0, len(paragraph), self.chunk_size)
        ]