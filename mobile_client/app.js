/**
 * FASHION MAROC — Client mobile hybride (HTML5 / JavaScript)
 * Pour livreurs et gérants — API REST Flask Q12
 */

/**
 * Backend API Flask — exécution locale (à adapter lors du déploiement API en production).
 */
const API_BASE = "http://127.0.0.1:5000/api/v1";

const ENDPOINTS = {
    produits: `${API_BASE}/produits`,
    alertes: `${API_BASE}/produits/alerte`,
    commandes: `${API_BASE}/commandes`,
    statistiques: `${API_BASE}/statistiques`,
};

// Panneaux
const PANELS = {
    catalogue: document.getElementById("panelCatalogue"),
    alertes: document.getElementById("panelAlertes"),
    commandes: document.getElementById("panelCommandes"),
    stats: document.getElementById("panelStats"),
};

// Éléments DOM
const catalogueList = document.getElementById("catalogueList");
const alertesList = document.getElementById("alertesList");
const commandesList = document.getElementById("commandesList");
const statsGrid = document.getElementById("statsGrid");
const catalogueEmpty = document.getElementById("catalogueEmpty");
const alertesEmpty = document.getElementById("alertesEmpty");
const commandesEmpty = document.getElementById("commandesEmpty");
const statsEmpty = document.getElementById("statsEmpty");
const badgeCatalogue = document.getElementById("badgeCatalogue");
const badgeAlertes = document.getElementById("badgeAlertes");
const badgeCommandes = document.getElementById("badgeCommandes");
const navAlertBadge = document.getElementById("navAlertBadge");
const errorBanner = document.getElementById("errorBanner");
const errorMessage = document.getElementById("errorMessage");
const loadingSpinner = document.getElementById("loadingSpinner");
const btnRefresh = document.getElementById("btnRefresh");

let ongletActif = "catalogue";

/** Libellés français des statuts commande */
const LIBELLES_STATUT = {
    EN_COURS: "En cours",
    "PARTIELLEMENT_REÇUE": "Partiellement reçue",
    "CLÔTURÉE": "Clôturée",
    EN_ATTENTE: "En attente",
    LIVREE: "Livrée",
};

const CLASSES_STATUT = {
    EN_COURS: "statut-warning",
    "PARTIELLEMENT_REÇUE": "statut-info",
    "CLÔTURÉE": "statut-success",
    EN_ATTENTE: "statut-secondary",
    LIVREE: "statut-success",
};

/**
 * Requête fetch avec gestion d'erreurs réseau et HTTP.
 */
async function appelerApi(url) {
    let response;
    try {
        response = await fetch(url, {
            method: "GET",
            headers: { Accept: "application/json" },
        });
    } catch {
        throw new Error(
            "Serveur Flask injoignable. Vérifiez que l'application tourne sur http://127.0.0.1:5000"
        );
    }

    let payload;
    try {
        payload = await response.json();
    } catch {
        throw new Error("Réponse du serveur invalide (JSON attendu).");
    }

    if (!response.ok) {
        const msg = payload.message || `Erreur HTTP ${response.status}`;
        throw new Error(msg);
    }

    return payload;
}

function afficherErreur(message) {
    errorMessage.textContent = message;
    errorBanner.classList.remove("d-none");
}

function masquerErreur() {
    errorBanner.classList.add("d-none");
}

function afficherChargement(visible) {
    loadingSpinner.classList.toggle("d-none", !visible);
}

function formaterPrix(prix) {
    if (prix === null || prix === undefined) return "—";
    return `${Number(prix).toLocaleString("fr-FR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })} MAD`;
}

function formaterDate(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
    });
}

function echapperHtml(texte) {
    const div = document.createElement("div");
    div.textContent = texte;
    return div.innerHTML;
}

function libelleStatut(statut) {
    return LIBELLES_STATUT[statut] || statut || "Inconnu";
}

function classeStatut(statut) {
    return CLASSES_STATUT[statut] || "statut-secondary";
}

/* ——— Catalogue ——— */

function creerCarteProduit(produit) {
    const card = document.createElement("article");
    card.className = "product-card";
    card.innerHTML = `
        <span class="card-ref">#${produit.id} · ${produit.reference || "N/A"}</span>
        <h3 class="card-title">${echapperHtml(produit.libelle || "Sans libellé")}</h3>
        <span class="card-price">${formaterPrix(produit.prix)}</span>
        <span class="card-stock">
            Stock : <strong>${produit.quantite_disponible ?? "—"}</strong> unités
        </span>
    `;
    return card;
}

function afficherCatalogue(produits) {
    catalogueList.innerHTML = "";
    badgeCatalogue.textContent = produits.length;

    if (produits.length === 0) {
        catalogueEmpty.classList.remove("d-none");
        return;
    }

    catalogueEmpty.classList.add("d-none");
    produits.forEach((p) => catalogueList.appendChild(creerCarteProduit(p)));
}

async function chargerCatalogue() {
    const payload = await appelerApi(ENDPOINTS.produits);
    const produits = payload.data || [];
    afficherCatalogue(produits);
    return produits;
}

/* ——— Alertes ——— */

function creerItemAlerte(produit) {
    const item = document.createElement("article");
    item.className = "alert-item";
    item.innerHTML = `
        <span class="alert-icon" aria-hidden="true">⚠️</span>
        <div class="alert-body">
            <h3>${echapperHtml(produit.libelle || "Produit")}</h3>
            <p>Réf. ${echapperHtml(produit.reference || "—")} · ID ${produit.id}</p>
            <p class="alert-qty">
                Stock critique : ${produit.quantite_disponible ?? 0} unité(s) restante(s)
            </p>
        </div>
    `;
    return item;
}

function afficherAlertes(produits) {
    alertesList.innerHTML = "";
    badgeAlertes.textContent = produits.length;

    if (produits.length > 0) {
        navAlertBadge.textContent = produits.length;
        navAlertBadge.classList.remove("d-none");
    } else {
        navAlertBadge.classList.add("d-none");
    }

    if (produits.length === 0) {
        alertesEmpty.classList.remove("d-none");
        return;
    }

    alertesEmpty.classList.add("d-none");
    produits.forEach((p) => alertesList.appendChild(creerItemAlerte(p)));
}

async function chargerAlertes() {
    const payload = await appelerApi(ENDPOINTS.alertes);
    const produits = payload.data || [];
    afficherAlertes(produits);
    return produits;
}

/* ——— Commandes ——— */

function creerCarteCommande(cmd) {
    const card = document.createElement("article");
    card.className = "commande-card";
    const statutClass = classeStatut(cmd.statut);
    card.innerHTML = `
        <div class="commande-top">
            <span class="commande-id">#${cmd.id_commande}</span>
            <span class="statut-badge ${statutClass}">${echapperHtml(libelleStatut(cmd.statut))}</span>
        </div>
        <h3 class="commande-fournisseur">${echapperHtml(cmd.nom_fournisseur || "Fournisseur inconnu")}</h3>
        <div class="commande-meta">
            <span><i class="bi bi-calendar3 me-1"></i>${formaterDate(cmd.date_commande)}</span>
            <span class="commande-montant">${formaterPrix(cmd.montant_total)}</span>
        </div>
    `;
    return card;
}

function afficherCommandes(commandes) {
    commandesList.innerHTML = "";
    badgeCommandes.textContent = commandes.length;

    if (commandes.length === 0) {
        commandesEmpty.classList.remove("d-none");
        return;
    }

    commandesEmpty.classList.add("d-none");
    commandes.forEach((c) => commandesList.appendChild(creerCarteCommande(c)));
}

async function chargerCommandes() {
    const payload = await appelerApi(ENDPOINTS.commandes);
    const commandes = payload.data || [];
    afficherCommandes(commandes);
    return commandes;
}

/* ——— Statistiques ——— */

function creerBlocStat(label, valeur, icone, variante) {
    const bloc = document.createElement("div");
    bloc.className = `stat-bloc stat-bloc-${variante}`;
    bloc.innerHTML = `
        <i class="bi ${icone} stat-icon"></i>
        <p class="stat-label">${label}</p>
        <p class="stat-valeur">${valeur}</p>
    `;
    return bloc;
}

function afficherStats(data) {
    statsGrid.innerHTML = "";

    if (!data) {
        statsEmpty.classList.remove("d-none");
        return;
    }

    statsEmpty.classList.add("d-none");

    statsGrid.appendChild(
        creerBlocStat("Total produits", data.total_produits, "bi-box-seam", "primary")
    );
    statsGrid.appendChild(
        creerBlocStat("Total alertes", data.total_alertes, "bi-exclamation-triangle", "danger")
    );
    statsGrid.appendChild(
        creerBlocStat("Produits sains", data.total_sains, "bi-check-circle", "success")
    );
    statsGrid.appendChild(
        creerBlocStat(
            "Taux d'alerte",
            `${data.taux_alerte_pct ?? 0} %`,
            "bi-percent",
            "accent"
        )
    );
}

async function chargerStats() {
    const payload = await appelerApi(ENDPOINTS.statistiques);
    afficherStats(payload.data);
    return payload.data;
}

/* ——— Navigation & chargement global ——— */

async function chargerOnglet(onglet) {
    afficherChargement(true);
    masquerErreur();

    try {
        switch (onglet) {
            case "catalogue":
                await chargerCatalogue();
                break;
            case "alertes":
                await chargerAlertes();
                break;
            case "commandes":
                await chargerCommandes();
                break;
            case "stats":
                await chargerStats();
                break;
            default:
                break;
        }
    } catch (err) {
        afficherErreur(err.message);
    } finally {
        afficherChargement(false);
    }
}

async function chargerDonnees() {
    afficherChargement(true);
    masquerErreur();

    try {
        await Promise.all([
            chargerCatalogue(),
            chargerAlertes(),
            chargerCommandes(),
            chargerStats(),
        ]);
    } catch (err) {
        afficherErreur(err.message);
    } finally {
        afficherChargement(false);
    }
}

function changerOnglet(onglet) {
    ongletActif = onglet;

    document.querySelectorAll(".bottom-nav .nav-item").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.tab === onglet);
    });

    Object.keys(PANELS).forEach((key) => {
        const panel = PANELS[key];
        const actif = key === onglet;
        panel.classList.toggle("d-none", !actif);
        panel.classList.toggle("active", actif);
    });

    chargerOnglet(onglet);
}

document.querySelectorAll(".bottom-nav .nav-item").forEach((btn) => {
    btn.addEventListener("click", () => changerOnglet(btn.dataset.tab));
});

btnRefresh.addEventListener("click", () => chargerDonnees());

document.addEventListener("DOMContentLoaded", () => {
    changerOnglet("catalogue");
});
