"""Scraper pour emploi-public.ma."""
from scrapers.base import BaseScraper
from models import Concours


def scrape_emploi_public(ministere: str, specialite: str, grade: str) -> list[Concours]:
    """Scrape les concours depuis emploi-public.ma."""
    scraper = BaseScraper()
    resultats = []

    # Recherche par mots-clés
    query = f"{grade} {specialite} {ministere}".replace(" ", "+")
    url = f"https://www.emploi-public.ma/fr/concoursListe.asp?c={query}"

    soup = scraper.fetch_page(url)
    if not soup:
        return resultats

    # Parser les résultats
    items = soup.select("table.tableauConcours tr") or soup.select(".concours-item")
    for item in items[:10]:
        try:
            lien = item.select_one("a[href]")
            if not lien:
                continue
            titre = lien.get_text(strip=True)
            href = lien.get("href", "")
            if not href.startswith("http"):
                href = f"https://www.emploi-public.ma/{href.lstrip('/')}"

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
