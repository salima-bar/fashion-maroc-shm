"""
Routes du module Rapports / Business Intelligence — Q11 (Bonus).
Agrégations SQL et visualisation Chart.js.
"""

import json

from flask import Blueprint, render_template
from sqlalchemy import case, func, select

from extensions import db
from models.categorie import Categorie
from models.produit import Produit
from models.stock import Stock

rapports_bp = Blueprint("rapports", __name__, url_prefix="/rapports")


def _calculer_valeur_stock_par_categorie():
    """
    Agrégation SQL : somme(quantite_disponible * prix_vente) par catégorie.
    """
    stmt = (
        select(
            Categorie.libelle_categorie,
            func.coalesce(
                func.sum(Stock.quantite_disponible * Produit.prix_vente), 0
            ).label("valeur_totale"),
        )
        .select_from(Categorie)
        .join(Produit, Produit.id_categorie == Categorie.id_categorie)
        .join(Stock, Stock.id_produit == Produit.id_produit)
        .group_by(Categorie.id_categorie, Categorie.libelle_categorie)
        .order_by(Categorie.libelle_categorie)
    )
    rows = db.session.execute(stmt).all()
    return {
        "labels": [r.libelle_categorie or "Sans libellé" for r in rows],
        "valeurs": [float(r.valeur_totale) for r in rows],
    }


def _calculer_proportion_alertes():
    """
    Agrégation SQL : nombre de produits en alerte vs produits sains.
    Alerte si quantite_disponible < seuil_minimum (même règle que est_en_alerte).
    """
    est_alerte = case(
        (
            (Stock.quantite_disponible.isnot(None))
            & (Stock.seuil_minimum.isnot(None))
            & (Stock.quantite_disponible < Stock.seuil_minimum),
            1,
        ),
        else_=0,
    )

    stmt = (
        select(
            func.sum(est_alerte).label("nb_alerte"),
            func.count(Produit.id_produit).label("nb_total"),
        )
        .select_from(Produit)
        .join(Stock, Stock.id_produit == Produit.id_produit)
    )
    row = db.session.execute(stmt).one()
    nb_alerte = int(row.nb_alerte or 0)
    nb_total = int(row.nb_total or 0)
    nb_sains = nb_total - nb_alerte

    return {
        "labels": ["Produits sains", "En alerte"],
        "valeurs": [nb_sains, nb_alerte],
        "nb_total": nb_total,
        "nb_alerte": nb_alerte,
        "nb_sains": nb_sains,
        "taux_alerte": round((nb_alerte / nb_total * 100), 1) if nb_total else 0,
    }


@rapports_bp.route("/")
def index():
    """Page Rapports avec graphiques Chart.js alimentés par la base PostgreSQL."""
    valeur_categories = _calculer_valeur_stock_par_categorie()
    proportion_alertes = _calculer_proportion_alertes()

    # Sérialisation JSON pour Chart.js (données dynamiques PostgreSQL)
    chart_valeur_json = json.dumps(valeur_categories, ensure_ascii=False)
    chart_alertes_json = json.dumps(proportion_alertes, ensure_ascii=False)

    valeur_totale_globale = sum(valeur_categories["valeurs"])

    return render_template(
        "rapports.html",
        chart_valeur_json=chart_valeur_json,
        chart_alertes_json=chart_alertes_json,
        valeur_totale_globale=valeur_totale_globale,
        nb_produits=proportion_alertes["nb_total"],
        nb_alertes=proportion_alertes["nb_alerte"],
        taux_alerte=proportion_alertes["taux_alerte"],
    )
