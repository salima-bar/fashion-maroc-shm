"""
Modèle ORM pour la table fournisseur (schéma cours_sql).
"""

from extensions import db


class Fournisseur(db.Model):
    """Fournisseur partenaire de FASHION MAROC."""

    __tablename__ = "fournisseur"
    __table_args__ = {"schema": "cours_sql"}

    id_fournisseur = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    adresse = db.Column(db.Text)

    # Relation : un fournisseur peut avoir plusieurs commandes
    commandes = db.relationship(
        "CommandeFournisseur", back_populates="fournisseur", lazy=True
    )

    def __repr__(self):
        return f"<Fournisseur {self.id_fournisseur} - {self.nom}>"
