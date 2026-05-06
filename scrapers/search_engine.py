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

    # Recherche bilingue : français et arabe
    # Dictionnaires de correspondance pour les ministères, spécialités, grades
    from config import MINISTERES, SPECIALITES, GRADES
    ARABIC_EQUIV = {
        "Ministère de la Santé": "وزارة الصحة",
        "Ministère de l'Intérieur": "وزارة الداخلية",
        "Ministère de l'Éducation Nationale": "وزارة التربية الوطنية",
        "Informatique": "المعلوميات",
        "Technicien 3ème grade": "تقني من الدرجة الثالثة",
        # ... ajoutez d'autres équivalents ici ...
    }
    terms_fr = " ".join(filter(None, [grade, specialite, ministere]))
    terms_ar = " ".join([ARABIC_EQUIV.get(x, x) for x in [grade, specialite, ministere] if x])

    queries = [
        # Français
        f'sujet épreuve concours {terms_fr} maroc filetype:pdf',
        f'QCM concours {terms_fr} maroc filetype:pdf',
        f'corrigé concours {terms_fr} fonction publique maroc',
        # Arabe
        f'موضوع مباراة التوظيف {terms_ar} المغرب',
        f'نماذج مباريات {terms_ar} الوظيفة العمومية',
        # Facebook, docs, forums (fr/ar)
        f'concours {terms_fr} maroc site:facebook.com sujet',
        f'مباراة {terms_ar} site:facebook.com موضوع',
        f'concours fonction publique maroc {terms_fr} site:facebook.com',
        f'concours {terms_fr} maroc site:scribd.com',
        f'concours {terms_fr} maroc site:slideshare.net',
        f'concours {terms_fr} maroc site:drive.google.com',
        f'sujet concours {terms_fr} maroc annales',
        f'concours {terms_fr} maroc épreuve écrite',
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
