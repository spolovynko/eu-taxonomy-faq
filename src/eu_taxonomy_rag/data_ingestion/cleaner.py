import re

from eu_taxonomy_rag.data_ingestion.schemas import FAQItem


class FAQCleaner:
    def clean(self, faqs: list[FAQItem]) -> list[FAQItem]:
        cleaned_faqs: list[FAQItem] = []
        seen_ids: set[str] = set()

        for faq in faqs:
            cleaned_faq = self._clean_faq(faq)

            if not cleaned_faq.question or not cleaned_faq.answer:
                continue

            if cleaned_faq.faq_id in seen_ids:
                continue

            seen_ids.add(cleaned_faq.faq_id)
            cleaned_faqs.append(cleaned_faq)

        return cleaned_faqs

    def _clean_faq(self, faq: FAQItem) -> FAQItem:
        return faq.model_copy(
            update={
                "faq_id": faq.faq_id.strip(),
                "section": self._normalize_text(faq.section),
                "question": self._normalize_text(faq.question),
                "answer": self._normalize_multiline_text(faq.answer),
                "source_url": faq.source_url.strip(),
            }
        )

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _normalize_multiline_text(self, value: str) -> str:
        paragraphs = re.split(r"\n+", value)

        cleaned_paragraphs = [
            self._normalize_text(paragraph)
            for paragraph in paragraphs
            if paragraph.strip()
        ]

        return "\n\n".join(cleaned_paragraphs)