from playwright.sync_api import sync_playwright

from eu_taxonomy_rag.scraper.base import Scraper


class PlaywrightScraper(Scraper):
    def fetch_html(self, url: str) -> str:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            try:
                page = browser.new_page()
                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=60_000,
                )

                page.locator(".ecl-accordion__item").first.wait_for(
                    state="attached",
                    timeout=30_000,
                )

                return page.content()
            finally:
                browser.close()