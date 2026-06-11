from pydantic import BaseModel


class FAQItem(BaseModel):
    faq_id: str
    section: str
    question: str
    answer: str
    source_url: str