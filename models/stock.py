"""
Modèle ORM pour la table stock (schéma cours_sql).
"""

from extensions import db


class Stock(db.Model):
    """Niveau de stock d'un produit en rayon."""

    __tablename__ = "stock"
    __table_args__ = {"schema": "cours_sql"}

    id_stock = db.Column(db.Integer, primary_key=True)
    quantite_disponible = db.Column(db.Integer)
    seuil_minimum = db.Column(db.Integer)
    emplacement_rayon = db.Column(db.String(20))
    id_produit = db.Column(
        db.Integer,
        db.ForeignKey("cours_sql.produit.id_produit"),
    )
    alerte = db.Column(db.String(50))

    # Relation : chaque ligne de stock est liée à un produit
    produit = db.relationship("Produit", back_populates="stock")

    @property
    def est_en_alerte(self):
        """
        Indique si le stock est sous le seuil minimum.
        True si quantite_disponible < seuil_minimum, False sinon.
        """
        if self.quantite_disponible is None or self.seuil_minimum is None:
            return False
        return self.quantite_disponible < self.seuil_minimum

    def __repr__(self):
        return f"<Stock {self.id_stock} - produit {self.id_produit}>"
