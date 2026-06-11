FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    EU_TAXONOMY_FAQ_URL=https://ec.europa.eu/sustainable-finance-taxonomy/faq \
    FAQ_OUTPUT_PATH=/app/data/raw/faqs.json \
    CHUNKS_OUTPUT_PATH=/app/data/processed/chunks.jsonl \
    CHUNK_SIZE=2000 \
    EMBEDDING_BASE_URL=http://ollama:11434/v1 \
    EMBEDDING_MODEL=qwen3-embedding:0.6b \
    EMBEDDING_BATCH_SIZE=32 \
    QDRANT_URL=http://qdrant:6333 \
    QDRANT_COLLECTION=eu_taxonomy_faq \
    TOP_K=5 \
    LLM_BASE_URL=http://ollama:11434/v1 \
    LLM_MODEL=qwen2.5:3b \
    LLM_TEMPERATURE=0

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-dev --no-install-project \
    && /app/.venv/bin/playwright install --with-deps chromium

COPY src ./src

RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["/app/.venv/bin/python", "-m", "eu_taxonomy_rag.main"]
