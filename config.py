"""Configuration du projet."""
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st

# Clé API Groq - supporte .env local ET Streamlit Cloud secrets
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") or st.secrets.get("GROQ_API_KEY", "")

# Modèle LLM à utiliser
LLM_MODEL = "llama-3.3-70b-versatile"

# Dossier de stockage des données
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Sources de scraping
SOURCES = [
    "https://www.emploi-public.ma",
    "https://www.men.gov.ma",
    "https://alwadifa-maroc.com",
]

# Liste des ministères
MINISTERES = [
    "Ministère de l'Éducation Nationale",
    "Ministère de la Santé",
    "Ministère de l'Intérieur",
    "Ministère de la Justice",
    "Ministère de l'Économie et des Finances",
    "Ministère de l'Agriculture",
    "Ministère de l'Équipement et de l'Eau",
    "Ministère de la Transition Énergétique",
    "Ministère de l'Industrie et du Commerce",
    "Ministère du Tourisme",
    "Ministère de la Culture",
    "Ministère de l'Enseignement Supérieur",
    "Ministère de la Jeunesse et des Sports",
    "Ministère des Affaires Étrangères",
    "Ministère de l'Emploi et de l'Insertion Professionnelle",
]

# Spécialités courantes
SPECIALITES = [
    "Sciences Économiques et Gestion",
    "Droit",
    "Informatique",
    "Sciences de l'Ingénieur",
    "Lettres et Sciences Humaines",
    "Sciences de la Vie et de la Terre",
    "Mathématiques",
    "Physique-Chimie",
    "Sciences Infirmières",
    "Architecture",
    "Génie Civil",
    "Comptabilité et Finance",
]

# Grades
GRADES = [
    "Technicien 3ème grade",
    "Technicien 4ème grade",
    "Administrateur 2ème grade",
    "Administrateur 3ème grade",
    "Ingénieur d'État 1er grade",
    "Rédacteur 3ème grade",
    "Adjoint Administratif 3ème grade",
    "Adjoint Technique 3ème grade",
    "Professeur de l'enseignement secondaire",
    "Médecin 1er grade",
]
