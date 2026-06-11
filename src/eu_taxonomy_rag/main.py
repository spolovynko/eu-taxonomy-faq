from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="EU Taxonomy FAQ")

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


def run():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
