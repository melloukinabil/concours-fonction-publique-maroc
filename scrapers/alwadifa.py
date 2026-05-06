"""Scraper pour alwadifa-maroc.com."""
from scrapers.base import BaseScraper
from models import Concours


def scrape_alwadifa(ministere: str, specialite: str, grade: str) -> list[Concours]:
    """Scrape les concours depuis alwadifa-maroc.com."""
    scraper = BaseScraper()
    resultats = []

    query = f"{grade} {specialite}".replace(" ", "+")
    url = f"https://alwadifa-maroc.com/?s={query}"

    soup = scraper.fetch_page(url)
    if not soup:
        return resultats

    articles = soup.select("article") or soup.select(".post")
    for article in articles[:10]:
        try:
            lien = article.select_one("a[href]")
            titre_el = article.select_one("h2, h3, .entry-title")
            if not lien or not titre_el:
                continue

            titre = titre_el.get_text(strip=True)
            href = lien.get("href", "")
            if not href.startswith("http"):
                href = f"https://alwadifa-maroc.com/{href.lstrip('/')}"

            concours = Concours(
                titre=titre,
                ministere=ministere,
                specialite=specialite,
                grade=grade,
                annee=2024,
                url_source=href,
            )
            resultats.append(concours)
        except Exception:
            continue

    return resultats
