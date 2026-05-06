"""Scraper de pages contenant des images de sujets de concours."""
import requests
import base64
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from models import Concours


def scrape_page_images(url: str) -> list[str]:
    """Extrait toutes les URLs d'images de sujets depuis une page web."""
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "lxml")

        image_urls = []

        # Chercher les images dans le contenu principal
        # Sites comme fctmaroc.com, blogspot, facebook posts
        selectors = [
            "article img",
            ".post-body img",
            ".entry-content img",
            ".post-content img",
            "#post-body img",
            ".blog-post img",
            "img[src*='blogger']",
            "img[src*='googleusercontent']",
            "img[src*='fbcdn']",
            "img[src*='scontent']",
        ]

        found_images = set()
        for selector in selectors:
            for img in soup.select(selector):
                src = img.get("src") or img.get("data-src") or ""
                # Prendre la version haute résolution si disponible
                if "blogger" in src or "googleusercontent" in src:
                    # Remplacer les paramètres de taille pour avoir l'image complète
                    src = src.split("=")[0] + "=s0" if "=" in src else src
                if src and src.startswith("http") and src not in found_images:
                    # Filtrer les petites icônes et logos
                    width = img.get("width", "")
                    height = img.get("height", "")
                    if width and int(width) < 100:
                        continue
                    if height and int(height) < 100:
                        continue
                    found_images.add(src)
                    image_urls.append(src)

        # Si pas trouvé avec les sélecteurs, chercher toutes les grandes images
        if not image_urls:
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src") or ""
                if src and src.startswith("http") and src not in found_images:
                    # Exclure les logos, icônes, avatars
                    exclude = ["logo", "icon", "avatar", "profile", "favicon", "badge"]
                    if any(ex in src.lower() for ex in exclude):
                        continue
                    found_images.add(src)
                    image_urls.append(src)

        return image_urls
    except Exception as e:
        print(f"[Erreur scrape images] {url}: {e}")
        return []


def download_image_as_base64(url: str) -> str | None:
    """Télécharge une image et la convertit en base64."""
    ua = UserAgent()
    try:
        response = requests.get(
            url,
            headers={"User-Agent": ua.random},
            timeout=15
        )
        if response.status_code == 200:
            return base64.b64encode(response.content).decode("utf-8")
    except Exception:
        pass
    return None


def get_image_mime_type(url: str) -> str:
    """Détermine le type MIME d'une image depuis son URL."""
    url_lower = url.lower()
    if ".png" in url_lower:
        return "image/png"
    elif ".gif" in url_lower:
        return "image/gif"
    elif ".webp" in url_lower:
        return "image/webp"
    return "image/jpeg"
