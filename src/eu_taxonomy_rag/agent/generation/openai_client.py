from collections.abc import Iterator

from openai import OpenAI as OpenAISDK

from eu_taxonomy_rag.agent.generation.llm_client import LLMClient
from eu_taxonomy_rag.agent.generation.prompt_builder import PromptBuilder
from eu_taxonomy_rag.agent.generation.schemas import RagAnswer
from eu_taxonomy_rag.agent.retrieval.schemas import RetrievedChunk


class OpenAIClient(LLMClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        temperature: float,
    ) -> None:
        if not 0 <= temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")

        self.client = OpenAISDK(
            base_url=base_url,
            api_key=api_key,
        )
        self.model = model
        self.temperature = temperature
        self.prompt_builder = PromptBuilder()

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> RagAnswer:
        system_prompt, user_prompt = self.prompt_builder.build(
            question=question,
            chunks=chunks,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("LLM returned an empty response")

        return RagAnswer.model_validate_json(content)

    def stream(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> Iterator[str]:
        system_prompt, user_prompt = self.prompt_builder.build_stream(
            question=question,
            chunks=chunks,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            stream=True,
        )

        for chunk in response:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content
