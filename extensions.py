"""
Extensions Flask partagées (instance SQLAlchemy unique).
Évite les imports circulaires et le double chargement de app.py.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
