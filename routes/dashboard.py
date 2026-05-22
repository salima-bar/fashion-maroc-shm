"""
Routes du tableau de bord (Dashboard) — Q7.
"""

from flask import Blueprint, render_template
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from extensions import db
from models.produit import Produit

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/")


@dashboard_bp.route("/")
def index():
    """
    Vue globale du tableau de bord : liste des produits et de leurs stocks.
    Requête exécutée via db.session dans le contexte Flask de la requête.
    """
    stmt = (
        select(Produit)
        .options(
            joinedload(Produit.stock),
            joinedload(Produit.categorie),
        )
        .order_by(Produit.id_produit)
    )
    produits = db.session.scalars(stmt).all()

    total_produits = len(produits)
    nb_alertes = sum(1 for p in produits if p.est_en_alerte)

    return render_template(
        "dashboard.html",
        produits=produits,
        total_produits=total_produits,
        nb_alertes=nb_alertes,
    )
