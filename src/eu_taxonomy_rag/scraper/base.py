from abc import ABC, abstractmethod


class Scraper(ABC):
    @abstractmethod
    def fetch_html(self, url: str) -> str:
        """Fetch and return the rendered FAQ page HTML."""