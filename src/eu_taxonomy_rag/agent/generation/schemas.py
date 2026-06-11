from typing import Literal

from pydantic import BaseModel, Field


class RagAnswer(BaseModel):
    answer: str = Field(min_length=1)
    confidence: Literal["low", "medium", "high"]
    used_chunk_ids: list[str]
    insufficient_context: bool
