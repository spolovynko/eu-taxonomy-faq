from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: str
    faq_id: str
    section: str
    question: str
    text_for_answering: str
    source_url: str
    score: float