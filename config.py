"""
Configuration de l'application FASHION MAROC.
Charge les variables sensibles depuis le fichier .env de manière sécurisée.
"""

import os

from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env (racine du projet)
load_dotenv()


def _normaliser_database_url(url):
    """
    Render fournit parfois postgres:// — SQLAlchemy attend postgresql://.
    """
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    """Classe de configuration centralisée pour Flask."""

    # URL PostgreSQL (.env local ou DATABASE_URL injectée par Render)
    SQLALCHEMY_DATABASE_URI = _normaliser_database_url(os.getenv("DATABASE_URL"))

    # Désactive le suivi des modifications (économie de ressources)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clé secrète Flask pour les sessions et la protection CSRF
    SECRET_KEY = os.getenv("SECRET_KEY", "cle-dev-a-remplacer")
