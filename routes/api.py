"""
API REST JSON FASHION MAROC — Q12 (Bonus).
Préfixe /api/v1 pour l'application mobile (déployée séparément sur Vercel).
"""

from flask import Blueprint, jsonify
from sqlalchemy import case, func, select
from sqlalchemy.orm import joinedload

from extensions import db
from models.commande_fournisseur import CommandeFournisseur
from models.produit import Produit
from models.stock import Stock

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.after_request
def ajouter_entetes_cors(response):
    """Autorise le client mobile (Vercel, localhost, Capacitor)."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept"
    return response


@api_bp.route("/produits", methods=["OPTIONS"])
@api_bp.route("/produits/alerte", methods=["OPTIONS"])
@api_bp.route("/commandes", methods=["OPTIONS"])
@api_bp.route("/statistiques", methods=["OPTIONS"])
def api_options():
    """Prévol CORS pour les clients hybrides."""
    return "", 204


def _serialiser_produit(produit):
    """Convertit un produit ORM en dictionnaire JSON."""
    quantite = None
    if produit.stock is not None:
        quantite = produit.stock.quantite_disponible

    prix = float(produit.prix_vente) if produit.prix_vente is not None else None

    return {
        "id": produit.id_produit,
        "reference": produit.reference,
        "libelle": produit.libelle,
        "prix": prix,
        "quantite_disponible": quantite,
    }


def _charger_produits_avec_stock():
    """Charge tous les produits avec leur stock associé."""
    stmt = (
        select(Produit)
        .options(joinedload(Produit.stock))
        .order_by(Produit.id_produit)
    )
    return db.session.scalars(stmt).unique().all()


@api_bp.route("/produits/alerte", methods=["GET"])
def produits_alerte():
    """
    GET /api/v1/produits/alerte
    Produits dont la quantité disponible est strictement inférieure au seuil.
    """
    produits = _charger_produits_avec_stock()
    alertes = [p for p in produits if p.est_en_alerte]

    if not alertes:
        return jsonify({
            "success": True,
            "message": "Aucun produit en alerte pour le moment.",
            "count": 0,
            "data": [],
        }), 200

    return jsonify({
        "success": True,
        "count": len(alertes),
        "data": [_serialiser_produit(p) for p in alertes],
    }), 200


@api_bp.route("/produits", methods=["GET"])
def liste_produits():
    """
    GET /api/v1/produits
    Liste complète des produits avec stock disponible.
    """
    produits = _charger_produits_avec_stock()

    if not produits:
        return jsonify({
            "success": False,
            "message": "Aucun produit trouvé en base de données.",
            "count": 0,
            "data": [],
        }), 404

    return jsonify({
        "success": True,
        "count": len(produits),
        "data": [_serialiser_produit(p) for p in produits],
    }), 200


@api_bp.route("/commandes", methods=["GET"])
def liste_commandes():
    """
    GET /api/v1/commandes
    Liste des commandes fournisseurs et leurs statuts.
    """
    stmt = (
        select(CommandeFournisseur)
        .options(joinedload(CommandeFournisseur.fournisseur))
        .order_by(CommandeFournisseur.id_commande)
    )
    commandes = db.session.scalars(stmt).unique().all()

    if not commandes:
        return jsonify({
            "success": False,
            "message": "Aucune commande fournisseur trouvée.",
            "count": 0,
            "data": [],
        }), 404

    data = []
    for cmd in commandes:
        data.append({
            "id_commande": cmd.id_commande,
            "date_commande": (
                cmd.date_commande.isoformat() if cmd.date_commande else None
            ),
            "statut": cmd.statut,
            "montant_total": (
                float(cmd.montant_total) if cmd.montant_total is not None else None
            ),
            "id_fournisseur": cmd.id_fournisseur,
            "nom_fournisseur": (
                cmd.fournisseur.nom if cmd.fournisseur else None
            ),
        })

    return jsonify({
        "success": True,
        "count": len(data),
        "data": data,
    }), 200


@api_bp.route("/statistiques", methods=["GET"])
def statistiques():
    """
    GET /api/v1/statistiques
    KPI globaux : total produits et total alertes.
    """
    total_produits = db.session.scalar(
        select(func.count(Produit.id_produit))
    ) or 0

    if total_produits == 0:
        return jsonify({
            "success": False,
            "message": "Aucune donnée statistique disponible.",
            "data": None,
        }), 404

    est_alerte = case(
        (
            (Stock.quantite_disponible.isnot(None))
            & (Stock.seuil_minimum.isnot(None))
            & (Stock.quantite_disponible < Stock.seuil_minimum),
            1,
        ),
        else_=0,
    )

    total_alertes = db.session.scalar(
        select(func.coalesce(func.sum(est_alerte), 0))
        .select_from(Produit)
        .join(Stock, Stock.id_produit == Produit.id_produit)
    ) or 0

    total_alertes = int(total_alertes)
    taux_alerte = round((total_alertes / total_produits) * 100, 1)

    return jsonify({
        "success": True,
        "data": {
            "total_produits": total_produits,
            "total_alertes": total_alertes,
            "total_sains": total_produits - total_alertes,
            "taux_alerte_pct": taux_alerte,
        },
    }), 200


@api_bp.errorhandler(404)
def api_not_found(error):
    """Réponse JSON uniforme pour les routes API introuvables."""
    return jsonify({
        "success": False,
        "message": "Ressource API introuvable.",
        "error": str(error),
    }), 404
