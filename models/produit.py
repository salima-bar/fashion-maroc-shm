"""
Modèle ORM pour la table produit (schéma cours_sql).
"""

from extensions import db


class Produit(db.Model):
    """Article de vêtement référencé en boutique."""

    __tablename__ = "produit"
    __table_args__ = {"schema": "cours_sql"}

    id_produit = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50))
    libelle = db.Column(db.String(150))
    prix_vente = db.Column(db.Numeric(10, 2))
    taille = db.Column(db.String(10))
    couleur = db.Column(db.String(30))
    id_categorie = db.Column(
        db.Integer,
        db.ForeignKey("cours_sql.categorie.id_categorie"),
    )

    # Relations
    categorie = db.relationship("Categorie", back_populates="produits")
    stock = db.relationship(
        "Stock", back_populates="produit", uselist=False, lazy=True
    )
    lignes_commande = db.relationship(
        "LigneCommande", back_populates="produit", lazy=True
    )

    @property
    def est_en_alerte(self):
        """
        Indique si le produit est en alerte stock.
        True si quantite_disponible < seuil_minimum, False sinon.
        """
        if self.stock is None:
            return False
        quantite = self.stock.quantite_disponible
        seuil = self.stock.seuil_minimum
        if quantite is None or seuil is None:
            return False
        return quantite < seuil

    def __repr__(self):
        return f"<Produit {self.id_produit} - {self.libelle}>"
