from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from eu_taxonomy_rag.api.routes import router
from eu_taxonomy_rag.observability import RequestLoggingMiddleware, configure_logging

STATIC_DIR = Path(__file__).parent.parent / "static"


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(title="EU Taxonomy FAQ")
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(router)
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app
