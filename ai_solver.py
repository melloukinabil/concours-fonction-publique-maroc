"""Générateur de solutions par IA (Groq - gratuit)."""
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL


def get_client() -> Groq:
    """Retourne le client Groq."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY manquante. Ajoutez-la dans le fichier .env")
    return Groq(api_key=GROQ_API_KEY)


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
