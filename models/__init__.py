"""
Package des modèles SQLAlchemy FASHION MAROC.
Importe toutes les classes pour les enregistrer auprès de l'objet db.
"""

from models.categorie import Categorie
from models.commande_fournisseur import CommandeFournisseur
from models.fournisseur import Fournisseur
from models.ligne_commande import LigneCommande
from models.produit import Produit
from models.stock import Stock

__all__ = [
    "Categorie",
    "Produit",
    "Fournisseur",
    "CommandeFournisseur",
    "LigneCommande",
    "Stock",
]
