"""Module de scraping des concours."""
from scrapers.emploi_public import scrape_emploi_public
from scrapers.alwadifa import scrape_alwadifa
from scrapers.search_engine import search_concours

__all__ = ["scrape_emploi_public", "scrape_alwadifa", "search_concours"]
