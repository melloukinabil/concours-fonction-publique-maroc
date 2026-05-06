"""Modèles de données pour les concours."""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Concours:
    """Représente un concours de la fonction publique."""
    titre: str
    ministere: str
    specialite: str
    grade: str
    annee: int
    date_concours: Optional[str] = None
    url_source: Optional[str] = None
    url_pdf: Optional[str] = None
    contenu_epreuve: Optional[str] = None
    solution_ia: Optional[str] = None
    date_scraping: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict) -> "Concours":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
