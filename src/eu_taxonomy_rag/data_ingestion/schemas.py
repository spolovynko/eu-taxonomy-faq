from pydantic import BaseModel


class FAQItem(BaseModel):
    faq_id: str
    section: str
    question: str
    answer: str
    source_url: str

class Chunk(BaseModel):
    chunk_id: str
    faq_id: str
    section: str
    question: str
    text_for_embedding: str
    text_for_answering: str
    source_url: str