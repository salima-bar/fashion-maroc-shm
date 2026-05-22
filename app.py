"""
Point d'entrée principal de l'application web FASHION MAROC.
Initialise Flask, SQLAlchemy et enregistre les Blueprints (Q5–Q7).
"""

from flask import Flask

from config import Config
from extensions import db


def create_app():
    """
    Factory d'application : garantit l'ordre d'initialisation correct
    (db.init_app → modèles → blueprints).
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # 1. Liaison SQLAlchemy à l'application Flask
    db.init_app(app)

    # 2. Enregistrement des modèles ORM (Q6)
    import models  # noqa: F401

    # 3. Enregistrement des Blueprints (Q7–Q8) — après db.init_app
    from routes.dashboard import dashboard_bp  # noqa: E402
    from routes.livraison import livraison_bp  # noqa: E402
    from routes.api import api_bp  # noqa: E402
    from routes.rapports import rapports_bp  # noqa: E402

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(livraison_bp)
    app.register_blueprint(rapports_bp)
    app.register_blueprint(api_bp)

    @app.template_filter("badge_statut")
    def badge_statut(statut):
        """Classe Bootstrap du badge selon le statut commande."""
        mapping = {
            "EN_COURS": "bg-warning text-dark",
            "PARTIELLEMENT_REÇUE": "bg-info text-dark",
            "CLÔTURÉE": "bg-success",
            "EN_ATTENTE": "bg-secondary",
            "LIVREE": "bg-success",
        }
        return mapping.get(statut, "bg-secondary")

    return app


# Instance utilisée par le serveur et les imports externes (flask run, etc.)
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
