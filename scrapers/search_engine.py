"""Recherche de sujets d'épreuves (les vrais examens avec questions) via DuckDuckGo."""
import requests
from urllib.parse import unquote, urlparse, parse_qs, quote
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from models import Concours


def _extract_real_url(ddg_url: str) -> str:
    """Extrait la vraie URL depuis un lien de redirection DuckDuckGo."""
    if "duckduckgo.com" in ddg_url or "uddg=" in ddg_url:
        parsed = urlparse(ddg_url)
        params = parse_qs(parsed.query)
        if "uddg" in params:
            return unquote(params["uddg"][0])
    return ddg_url


def search_concours(ministere: str, specialite: str, grade: str) -> list[Concours]:
    """Recherche des SUJETS D'ÉPREUVES (questions d'examen) pas des annonces."""
    resultats = []
    ua = UserAgent()

    # Requêtes ciblées sur les SUJETS avec questions (pas les annonces)
    queries = [
        f'"sujet" "épreuve" concours {grade} {specialite} maroc filetype:pdf',
        f'"QCM" concours {specialite} fonction publique maroc filetype:pdf',
        f'"corrigé" concours {grade} {specialite} maroc filetype:pdf',
        f'موضوع مباراة {specialite} {grade} maroc filetype:pdf',
        f'sujet concours {specialite} maroc site:scribd.com OR site:calameo.com OR site:drive.google.com',
    ]

    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html",
    }

    for query in queries:
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            links = soup.select("a.result__a")
            for link in links[:8]:
                titre = link.get_text(strip=True)
                href = link.get("href", "")
                href = _extract_real_url(href)

                # Ne garder que les URLs absolues valides
                if not href.startswith("http"):
                    continue

                # Exclure les sites d'annonces (on veut les sujets, pas les annonces)
                sites_annonces = ["emploi-public.ma", "alwadifa", "dreamjob", "linkedin", "rekrute"]
                if any(site in href.lower() for site in sites_annonces):
                    continue

                # Éviter les doublons
                if any(r.url_source == href for r in resultats):
                    continue

                is_pdf = href.lower().endswith(".pdf")
                concours = Concours(
                    titre=titre,
                    ministere=ministere,
                    specialite=specialite,
                    grade=grade,
                    annee=2024,
                    url_source=href,
                    url_pdf=href if is_pdf else None,
                )
                resultats.append(concours)
        except Exception as e:
            print(f"[Erreur recherche] {e}")

    return resultats
