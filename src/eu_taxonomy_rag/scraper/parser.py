from hashlib import sha1

from bs4 import BeautifulSoup, Tag

from eu_taxonomy_rag.data_ingestion import FAQItem


class Parser:
    def parse(self, html: str, source_url: str) -> list[FAQItem]:
        soup = BeautifulSoup(html, "html.parser")
        faqs: list[FAQItem] = []
        section = "Uncategorized"

        elements = soup.select(
            "h2.ecl-u-type-heading-2, .ecl-accordion__item"
        )

        for element in elements:
            if element.name == "h2":
                section = self._clean_text(element)
                continue

            faq = self._parse_item(element, section, source_url)

            if faq is not None:
                faqs.append(faq)

        return faqs

    def _parse_item(
        self,
        element: Tag,
        section: str,
        source_url: str,
    ) -> FAQItem | None:
        question_element = element.select_one(
            ".ecl-accordion__toggle-title"
        )
        answer_element = element.select_one(".faq-answer")

        if question_element is None or answer_element is None:
            return None

        question = self._clean_text(question_element)
        answer = self._clean_multiline_text(answer_element)

        if not question or not answer:
            return None

        return FAQItem(
            faq_id=self._create_faq_id(section, question),
            section=section,
            question=question,
            answer=answer,
            source_url=source_url,
        )

    def _create_faq_id(self, section: str, question: str) -> str:
        value = f"{section}|{question}".encode("utf-8")
        digest = sha1(value).hexdigest()[:12]

        return f"faq_{digest}"

    def _clean_text(self, element: Tag) -> str:
        return " ".join(element.get_text(" ", strip=True).split())

    def _clean_multiline_text(self, element: Tag) -> str:
        paragraphs = element.select("p, li")

        if not paragraphs:
            return self._clean_text(element)

        cleaned = [
            self._clean_text(paragraph)
            for paragraph in paragraphs
        ]

        return "\n".join(text for text in cleaned if text)