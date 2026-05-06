"""Générateur de solutions par IA (Groq - gratuit)."""
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

# Modèle avec support vision pour lire les images
VISION_MODEL = "llama-3.2-90b-vision-preview"


def get_client() -> Groq:
    """Retourne le client Groq."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY manquante. Ajoutez-la dans le fichier .env")
    return Groq(api_key=GROQ_API_KEY)


def lire_image_concours(image_base64: str, mime_type: str = "image/jpeg") -> str:
    """Utilise l'IA vision pour lire et extraire le texte d'une image de concours."""
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extrais tout le texte de cette image de sujet de concours marocain. Reproduis fidèlement les questions, les choix (si QCM), et toutes les informations visibles (ministère, grade, date, durée). Réponds uniquement avec le contenu extrait."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lecture image: {e}"


def generer_solution(contenu_epreuve: str, specialite: str, grade: str) -> str:
    """Génère une solution détaillée pour une épreuve de concours."""
    client = get_client()

    prompt = f"""Tu es un expert en préparation aux concours de la fonction publique marocaine.
Voici une épreuve de concours pour le grade "{grade}" dans la spécialité "{specialite}".

ÉPREUVE:
{contenu_epreuve}

INSTRUCTIONS:
- Fournis une solution complète, détaillée et structurée
- Explique chaque étape de raisonnement
- Utilise un langage clair et professionnel
- Si c'est un QCM, justifie chaque réponse
- Si c'est une rédaction, propose un plan détaillé avec développement
- Ajoute des conseils méthodologiques pour le candidat

SOLUTION DÉTAILLÉE:"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en concours de la fonction publique marocaine. Tu réponds en français."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de la génération de la solution: {e}"


def resumer_concours(contenu: str) -> str:
    """Résume le contenu d'un concours (matières, durée, barème)."""
    client = get_client()

    prompt = f"""Résume ce document de concours de la fonction publique marocaine.
Extrais: matières, durée, barème, conditions d'accès, date.

DOCUMENT:
{contenu[:3000]}

RÉSUMÉ STRUCTURÉ:"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur: {e}"
