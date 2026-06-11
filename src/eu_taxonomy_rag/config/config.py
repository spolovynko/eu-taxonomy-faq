from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    port: int
    eu_taxonomy_faq_url: str
    faq_output_path: Path
    chunks_output_path: Path
    chunk_size: int
    embedding_base_url: str
    embedding_api_key: str
    embedding_model: str
    embedding_batch_size: int
    qdrant_url: str
    qdrant_collection: str
    top_k: int
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    llm_temperature: float

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("host")
    @classmethod
    def validate_host(cls, value: str) -> str:
        host = value.strip()
        if not host:
            raise ValueError("HOST cannot be empty")
        return host

    @field_validator("port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        if not 1 <= value <= 65535:
            raise ValueError("PORT must be between 1 and 65535")

        return value

    @field_validator("eu_taxonomy_faq_url")
    @classmethod
    def validate_faq_url(cls, value: str) -> str:
        url = value.strip()

        if not url.startswith(("http://", "https://")):
            raise ValueError("EU_TAXONOMY_FAQ_URL must be a valid URL")

        return url

    @field_validator("faq_output_path", mode="before")
    @classmethod
    def validate_faq_output_path(cls, value: str | Path) -> Path:
        output_path = Path(value)

        if output_path.suffix.lower() != ".json":
            raise ValueError("FAQ_OUTPUT_PATH must point to a JSON file")

        return output_path

    @field_validator("chunks_output_path", mode="before")
    @classmethod
    def validate_chunks_output_path(cls, value: str | Path) -> Path:
        output_path = Path(value)

        if output_path.suffix.lower() != ".jsonl":
            raise ValueError("CHUNKS_OUTPUT_PATH must point to a JSONL file")

        return output_path

    @field_validator("chunk_size")
    @classmethod
    def validate_chunk_size(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("CHUNK_SIZE must be greater than zero")

        return value

    @field_validator("embedding_base_url")
    @classmethod
    def validate_embedding_base_url(cls, value: str) -> str:
        base_url = value.strip().rstrip("/")

        if not base_url.startswith(("http://", "https://")):
            raise ValueError("EMBEDDING_BASE_URL must be a valid URL")

        return base_url

    @field_validator("embedding_api_key", "embedding_model")
    @classmethod
    def validate_embedding_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Embedding configuration values cannot be empty")

        return value

    @field_validator("embedding_batch_size")
    @classmethod
    def validate_embedding_batch_size(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("EMBEDDING_BATCH_SIZE must be greater than zero")

        return value

    @field_validator("qdrant_url")
    @classmethod
    def validate_qdrant_url(cls, value: str) -> str:
        url = value.strip().rstrip("/")

        if not url.startswith(("http://", "https://")):
            raise ValueError("QDRANT_URL must be a valid URL")

        return url

    @field_validator("qdrant_collection")
    @classmethod
    def validate_qdrant_collection(cls, value: str) -> str:
        collection = value.strip()

        if not collection:
            raise ValueError("QDRANT_COLLECTION cannot be empty")

        return collection

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("TOP_K must be greater than zero")

        return value

    @field_validator("llm_base_url")
    @classmethod
    def validate_llm_base_url(cls, value: str) -> str:
        base_url = value.strip().rstrip("/")

        if not base_url.startswith(("http://", "https://")):
            raise ValueError("LLM_BASE_URL must be a valid URL")

        return base_url

    @field_validator("llm_api_key", "llm_model")
    @classmethod
    def validate_llm_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("LLM configuration values cannot be empty")

        return value

    @field_validator("llm_temperature")
    @classmethod
    def validate_llm_temperature(cls, value: float) -> float:
        if not 0 <= value <= 2:
            raise ValueError("LLM_TEMPERATURE must be between 0 and 2")

        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
