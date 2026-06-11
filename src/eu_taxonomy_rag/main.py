from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from eu_taxonomy_rag.config import get_settings

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="EU Taxonomy FAQ")

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


def run():
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
