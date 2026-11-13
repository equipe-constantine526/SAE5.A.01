"""Point d'entrée du backend RigMatch.

Lancer : flask --app app run --debug   (ou : python app.py)
"""
from flask import Flask, jsonify
from flask_cors import CORS

from controllers.composants import bp as composants_bp
from controllers.recommandation import bp as recommandation_bp
from controllers.configs import bp as configs_bp
from controllers.stats import bp as stats_bp


def create_app():
    app = Flask(__name__)

    # Le front (Vue, port 5173) et le back (Flask, port 5000) sont sur deux ports différents.
    # Sans CORS, le navigateur bloque toutes les requêtes du front. (tâche 34)
    CORS(app)

    # Chaque controller est un "blueprint" : un groupe de routes rangé dans son propre fichier.
    app.register_blueprint(composants_bp)
    app.register_blueprint(recommandation_bp)
    app.register_blueprint(configs_bp)
    app.register_blueprint(stats_bp)

    @app.get("/api/health")
    def health():
        """Route de test : si elle répond, le serveur tourne."""
        return jsonify({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
