"""
Routes du module de réception des livraisons — Q8.
Gestion transactionnelle atomique des réceptions fournisseur.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from extensions import db
from models.commande_fournisseur import CommandeFournisseur
from models.ligne_commande import LigneCommande
from models.stock import Stock

livraison_bp = Blueprint("livraison", __name__, url_prefix="/livraisons")

# Statuts métier du TP
STATUT_EN_COURS = "EN_COURS"
STATUT_PARTIEL = "PARTIELLEMENT_REÇUE"
STATUT_CLOTUREE = "CLÔTURÉE"

STATUTS_RECEPTIONNABLES = (STATUT_EN_COURS, STATUT_PARTIEL)


@livraison_bp.route("/")
def index():
    """Liste des commandes fournisseurs à réceptionner."""
    stmt = (
        select(CommandeFournisseur)
        .where(CommandeFournisseur.statut.in_(STATUTS_RECEPTIONNABLES))
        .options(
            joinedload(CommandeFournisseur.fournisseur),
            joinedload(CommandeFournisseur.lignes),
        )
        .order_by(CommandeFournisseur.date_commande.desc())
    )
    commandes = db.session.scalars(stmt).unique().all()

    return render_template("livraisons.html", commandes=commandes)


@livraison_bp.route("/recevoir/<int:id_commande>", methods=["GET"])
def recevoir(id_commande):
    """Formulaire détaillé de réception pour une commande."""
    commande = db.session.scalar(
        select(CommandeFournisseur)
        .where(CommandeFournisseur.id_commande == id_commande)
        .options(
            joinedload(CommandeFournisseur.fournisseur),
            joinedload(CommandeFournisseur.lignes).joinedload(LigneCommande.produit),
        )
    )

    if commande is None:
        flash("Commande introuvable.", "danger")
        return redirect(url_for("livraison.index"))

    if commande.statut not in STATUTS_RECEPTIONNABLES:
        flash(
            f"Cette commande n'est plus réceptionnable (statut : {commande.statut}).",
            "warning",
        )
        return redirect(url_for("livraison.index"))

    return render_template("detail_livraison.html", commande=commande)


@livraison_bp.route("/recevoir/<int:id_commande>", methods=["POST"])
def traiter_reception(id_commande):
    """
    Traite la réception de manière atomique :
    mise à jour stock + lignes + statut commande en une seule transaction.
    """
    try:
        commande = db.session.scalar(
            select(CommandeFournisseur)
            .where(CommandeFournisseur.id_commande == id_commande)
            .options(
                joinedload(CommandeFournisseur.lignes).joinedload(
                    LigneCommande.produit
                ),
            )
        )

        if commande is None:
            raise ValueError("Commande introuvable.")

        if commande.statut not in STATUTS_RECEPTIONNABLES:
            raise ValueError(
                f"Réception impossible : statut actuel « {commande.statut} »."
            )

        au_moins_une_reception = False

        for ligne in commande.lignes:
            champ = f"quantite_{ligne.id_ligne}"
            valeur = request.form.get(champ, "").strip()

            if not valeur:
                continue

            try:
                quantite_saisie = int(valeur)
            except ValueError as err:
                raise ValueError(
                    f"Quantité invalide pour la ligne {ligne.id_ligne}."
                ) from err

            if quantite_saisie < 0:
                raise ValueError(
                    f"La quantité reçue ne peut pas être négative (ligne {ligne.id_ligne})."
                )

            if quantite_saisie == 0:
                continue

            quantite_deja_recue = ligne.quantite_recue or 0
            quantite_commandee = ligne.quantite_commandee or 0
            reste_a_recevoir = quantite_commandee - quantite_deja_recue

            if quantite_saisie > reste_a_recevoir:
                raise ValueError(
                    f"Quantité trop élevée pour « {ligne.produit.libelle if ligne.produit else 'produit'} » "
                    f"(reste à recevoir : {reste_a_recevoir})."
                )

            # Écart = quantité reçue lors de cette réception
            ecart = quantite_saisie

            ligne.quantite_recue = quantite_deja_recue + ecart

            stock = db.session.scalar(
                select(Stock).where(Stock.id_produit == ligne.id_produit)
            )
            if stock is None:
                raise ValueError(
                    f"Aucun stock trouvé pour le produit ID {ligne.id_produit}."
                )

            stock.quantite_disponible = (stock.quantite_disponible or 0) + ecart
            au_moins_une_reception = True

        if not au_moins_une_reception:
            raise ValueError(
                "Veuillez saisir au moins une quantité reçue supérieure à zéro."
            )

        # Mise à jour du statut global de la commande
        toutes_recues = all(
            (l.quantite_recue or 0) >= (l.quantite_commandee or 0)
            for l in commande.lignes
        )

        if toutes_recues:
            commande.statut = STATUT_CLOTUREE
        else:
            commande.statut = STATUT_PARTIEL

        db.session.commit()
        flash(
            f"Réception enregistrée avec succès pour la commande #{id_commande}.",
            "success",
        )
        return redirect(url_for("livraison.index"))

    except Exception as exc:
        db.session.rollback()
        flash(f"Échec de la réception : {exc}", "danger")
        return redirect(url_for("livraison.recevoir", id_commande=id_commande))
