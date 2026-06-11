from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    port: int
    eu_taxonomy_faq_url: str
    faq_output_path: Path

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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
