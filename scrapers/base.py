"""Classe de base pour les scrapers."""
import time
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class BaseScraper:
    """Scraper de base avec gestion des headers et délais."""

    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()

    def get_headers(self) -> dict:
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,ar;q=0.8",
        }

    def fetch_page(self, url: str) -> BeautifulSoup | None:
        """Récupère et parse une page HTML."""
        try:
            time.sleep(random.uniform(1, 3))  # Délai anti-ban
            response = self.session.get(url, headers=self.get_headers(), timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, "lxml")
        except Exception as e:
            print(f"[Erreur scraping] {url}: {e}")
            return None

    def download_pdf(self, url: str, filepath: str) -> bool:
        """Télécharge un fichier PDF."""
        try:
            response = self.session.get(url, headers=self.get_headers(), timeout=30)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"[Erreur PDF] {url}: {e}")
            return False
