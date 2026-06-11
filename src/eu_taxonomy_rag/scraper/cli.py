import json
from pathlib import Path

from eu_taxonomy_rag.config import get_settings
from eu_taxonomy_rag.scraper import (
    Parser,
    PlaywrightScraper,
    Scraper,
)


def scrape_faqs(
    scraper: Scraper,
    parser: Parser,
    url: str,
    output_path: Path,
) -> None:
    html = scraper.fetch_html(url)
    faqs = parser.parse(html, url)

    if not faqs:
        raise RuntimeError("No FAQ entries were found on the page")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            [faq.model_dump() for faq in faqs],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Extracted FAQs: {len(faqs)}")
    print(f"Saved to: {output_path}")


def main() -> None:
    settings = get_settings()

    scrape_faqs(
        scraper=PlaywrightScraper(),
        parser=Parser(),
        url=settings.eu_taxonomy_faq_url,
        output_path=settings.faq_output_path,
    )


if __name__ == "__main__":
    main()
