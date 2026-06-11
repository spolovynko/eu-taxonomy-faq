from eu_taxonomy_rag.api import create_app
from eu_taxonomy_rag.config import get_settings

app = create_app()


def run():
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
