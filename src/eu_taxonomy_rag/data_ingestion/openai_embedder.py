from openai import OpenAI

from eu_taxonomy_rag.data_ingestion.embedder import Embedder


class OpenAIEmbedder(Embedder):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        batch_size: int,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model = model
        self.batch_size = batch_size

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        vectors: list[list[float]] = []

        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            response = self.client.embeddings.create(
                model=self.model,
                input=batch,
            )

            vectors.extend(
                item.embedding
                for item in sorted(
                    response.data,
                    key=lambda item: item.index,
                )
            )

        if len(vectors) != len(texts):
            raise RuntimeError("Embedding response count does not match input count")

        return vectors

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=[text],
        )

        return response.data[0].embedding
