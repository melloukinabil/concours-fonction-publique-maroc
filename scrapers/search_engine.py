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
    """Recherche des SUJETS D'ÉPREUVES depuis plusieurs sources incluant Facebook."""
    resultats = []
    ua = UserAgent()

    # Construire les termes de recherche
    terms = " ".join(filter(None, [grade, specialite, ministere]))

    # Requêtes variées pour maximiser les résultats
    queries = [
        # PDFs de sujets - requêtes larges
        f'sujet épreuve concours {terms} maroc filetype:pdf',
        f'QCM concours {terms} maroc filetype:pdf',
        f'corrigé concours {terms} fonction publique maroc',
        # Recherche en arabe
        f'موضوع مباراة التوظيف {terms} maroc',
        f'نماذج مباريات {specialite} الوظيفة العمومية',
        # Facebook - groupes de partage de sujets
        f'concours {terms} maroc site:facebook.com sujet',
        f'مباراة {specialite} site:facebook.com موضوع',
        f'concours fonction publique maroc {specialite} site:facebook.com',
        # Sites de partage de documents
        f'concours {terms} maroc site:scribd.com',
        f'concours {terms} maroc site:slideshare.net',
        f'concours {terms} maroc site:drive.google.com',
        # Blogs et forums marocains
        f'sujet concours {terms} maroc annales',
        f'concours {terms} maroc épreuve écrite',
        # Sans filetype pour élargir
        f'concours {specialite} fonction publique maroc sujet questions',
    ]

    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html",
        "Accept-Language": "fr-FR,fr;q=0.9,ar;q=0.8",
    }

    seen_urls = set()

    for query in queries:
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.text, "lxml")

            links = soup.select("a.result__a")
            snippets = soup.select(".result__snippet")

            for idx, link in enumerate(links[:8]):
                titre = link.get_text(strip=True)
                href = link.get("href", "")
                href = _extract_real_url(href)

                # Ne garder que les URLs absolues valides
                if not href.startswith("http"):
                    continue

                # Éviter les doublons
                if href in seen_urls:
                    continue
                seen_urls.add(href)

                # Exclure les sites sans contenu utile
                sites_exclus = ["rekrute.com", "linkedin.com", "indeed.com"]
                if any(site in href.lower() for site in sites_exclus):
                    continue

                # Récupérer le snippet comme description
                description = ""
                if idx < len(snippets):
                    description = snippets[idx].get_text(strip=True)

                is_pdf = href.lower().endswith(".pdf")
                concours = Concours(
                    titre=titre,
                    ministere=ministere,
                    specialite=specialite,
                    grade=grade,
                    annee=2024,
                    url_source=href,
                    url_pdf=href if is_pdf else None,
                    contenu_epreuve=description,
                )
                resultats.append(concours)
        except Exception:
            continue

    return resultats
