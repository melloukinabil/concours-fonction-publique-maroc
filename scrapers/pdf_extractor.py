"""Extraction de texte depuis les PDFs de concours."""
import os
import PyPDF2
from scrapers.base import BaseScraper
from config import DATA_DIR


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrait le texte d'un fichier PDF local."""
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[Erreur PDF] {pdf_path}: {e}")
    return text.strip()


def download_and_extract(url: str, filename: str) -> str:
    """Télécharge un PDF et extrait son contenu textuel."""
    scraper = BaseScraper()
    filepath = os.path.join(DATA_DIR, filename)

    if os.path.exists(filepath):
        return extract_text_from_pdf(filepath)

    if scraper.download_pdf(url, filepath):
        return extract_text_from_pdf(filepath)

    return ""
