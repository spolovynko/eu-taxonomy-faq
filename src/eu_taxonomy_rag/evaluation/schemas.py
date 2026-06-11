from pydantic import BaseModel, Field, model_validator


class EvaluationQuestion(BaseModel):
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    expected_faq_ids: list[str]
    answerable: bool

    @model_validator(mode="after")
    def validate_expected_faq_ids(self):
        if self.answerable and not self.expected_faq_ids:
            raise ValueError("Answerable questions need an expected FAQ ID")

        if not self.answerable and self.expected_faq_ids:
            raise ValueError("Unanswerable questions cannot have expected FAQ IDs")

        return self


class AnswerEvaluationQuestion(BaseModel):
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    expected_faq_ids: list[str]
    expected_facts: list[list[str]]
    answerable: bool
    variant_group: str | None = None

    @model_validator(mode="after")
    def validate_expected_values(self):
        if self.answerable:
            if not self.expected_faq_ids:
                raise ValueError("Answerable questions need an expected FAQ ID")

            if not self.expected_facts:
                raise ValueError("Answerable questions need expected facts")
        elif self.expected_faq_ids or self.expected_facts:
            raise ValueError(
                "Unanswerable questions cannot have expected FAQs or facts"
            )

        return self
