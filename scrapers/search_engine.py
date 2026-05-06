"""Recherche de sujets d'épreuves de concours via DuckDuckGo (gratuit, sans API key)."""
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from models import Concours

# Mots-clés qui indiquent un vrai sujet d'épreuve (pas des consignes admin)
MOTS_EPREUVE = ["sujet", "épreuve", "qcm", "examen", "corrigé", "annale", "امتحان", "موضوع"]
# Mots-clés à exclure (documents administratifs)
MOTS_EXCLUS = ["تشريع", "consigne", "circulaire", "note", "مذكرة", "décret", "arrêté"]


def is_sujet_epreuve(titre: str, url: str) -> bool:
    """Vérifie si le résultat est un vrai sujet d'épreuve et non un doc admin."""
    texte = (titre + " " + url).lower()
    # Exclure les documents administratifs
    for mot in MOTS_EXCLUS:
        if mot.lower() in texte:
            return False
    # Privilégier les vrais sujets
    for mot in MOTS_EPREUVE:
        if mot.lower() in texte:
            return True
    # Si c'est un PDF avec "concours" c'est potentiellement un sujet
    if ".pdf" in url and "concours" in texte:
        return True
    return False


def search_concours(ministere: str, specialite: str, grade: str) -> list[Concours]:
    """Recherche des sujets d'épreuves via DuckDuckGo HTML (gratuit, pas d'API)."""
    resultats = []
    ua = UserAgent()

    # Requêtes ciblées sur les SUJETS d'épreuves
    queries = [
        f"sujet épreuve concours {grade} {specialite} {ministere} maroc filetype:pdf",
        f"QCM concours {grade} {specialite} maroc filetype:pdf",
        f"annales corrigé concours {specialite} fonction publique maroc",
    ]

    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html",
    }

    for query in queries:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            links = soup.select("a.result__a")
            for link in links[:10]:
                titre = link.get_text(strip=True)
                href = link.get("href", "")

                # Filtrer : garder uniquement les vrais sujets d'épreuves
                if not is_sujet_epreuve(titre, href):
                    continue

                # Éviter les doublons
                if any(r.url_source == href for r in resultats):
                    continue

                concours = Concours(
                    titre=titre,
                    ministere=ministere,
                    specialite=specialite,
                    grade=grade,
                    annee=2024,
                    url_source=href,
                    url_pdf=href if href.endswith(".pdf") else None,
                )
                resultats.append(concours)
        except Exception as e:
            print(f"[Erreur recherche] {e}")

    return resultats
