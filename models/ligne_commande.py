"""
Modèle ORM pour la table ligne_commande (schéma cours_sql).
"""

from extensions import db


class LigneCommande(db.Model):
    """Ligne détaillant un produit commandé chez un fournisseur."""

    __tablename__ = "ligne_commande"
    __table_args__ = {"schema": "cours_sql"}

    id_ligne = db.Column(db.Integer, primary_key=True)
    quantite_commandee = db.Column(db.Integer)
    prix_unitaire_achat = db.Column(db.Numeric(10, 2))
    quantite_recue = db.Column(db.Integer)
    id_commande = db.Column(
        db.Integer,
        db.ForeignKey("cours_sql.commande_fournisseur.id_commande"),
    )
    id_produit = db.Column(
        db.Integer,
        db.ForeignKey("cours_sql.produit.id_produit"),
    )
    livraison = db.Column(db.String(50))

    # Relations
    commande = db.relationship("CommandeFournisseur", back_populates="lignes")
    produit = db.relationship("Produit", back_populates="lignes_commande")

    def __repr__(self):
        return f"<LigneCommande {self.id_ligne} - commande {self.id_commande}>"
