"""
Modèle ORM pour la table categorie (schéma cours_sql).
"""

from extensions import db


class Categorie(db.Model):
    """Catégorie de vêtements (Hauts, Bas, Chaussures, etc.)."""

    __tablename__ = "categorie"
    __table_args__ = {"schema": "cours_sql"}

    id_categorie = db.Column(db.Integer, primary_key=True)
    libelle_categorie = db.Column(db.String(100))
    description = db.Column(db.Text)

    # Relation : une catégorie regroupe plusieurs produits
    produits = db.relationship("Produit", back_populates="categorie", lazy=True)

    def __repr__(self):
        return f"<Categorie {self.id_categorie} - {self.libelle_categorie}>"
