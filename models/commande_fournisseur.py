"""
Modèle ORM pour la table commande_fournisseur (schéma cours_sql).
"""

from extensions import db


class CommandeFournisseur(db.Model):
    """Commande passée auprès d'un fournisseur."""

    __tablename__ = "commande_fournisseur"
    __table_args__ = {"schema": "cours_sql"}

    id_commande = db.Column(db.Integer, primary_key=True)
    date_commande = db.Column(db.Date)
    statut = db.Column(db.String(50))
    montant_total = db.Column(db.Numeric(10, 2))
    date_livraison_prev = db.Column(db.Date)
    id_fournisseur = db.Column(
        db.Integer,
        db.ForeignKey("cours_sql.fournisseur.id_fournisseur"),
    )

    # Relations
    fournisseur = db.relationship("Fournisseur", back_populates="commandes")
    lignes = db.relationship(
        "LigneCommande", back_populates="commande", lazy=True
    )

    def __repr__(self):
        return f"<CommandeFournisseur {self.id_commande} - {self.statut}>"
