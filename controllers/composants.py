"""Recherche de composants pour l'autocomplétion du formulaire.

Responsable : A2 (tâche 9).

Un controller ne calcule rien : il lit la requête, appelle un service, renvoie du JSON.
"""
from flask import Blueprint, jsonify, request

from services import compatibilite

bp = Blueprint("composants", __name__, url_prefix="/api")

TYPES_VALIDES = {"cpu", "carte_mere", "ram", "gpu", "alim", "boitier"}


@bp.get("/composants")
def rechercher():
    """Recherche des composants par type et nom pour l'autocomplétion.

    **Reçoit :** paramètres HTTP `type` (ex. `"gpu"`) et `q` (ex. `"4070"`).

    **Renvoie :** liste JSON `[{"id", "nom", "prix"}]` (20 max), ou une erreur
    `400` avec `{"erreur": "..."}` si le type est absent ou invalide.

    **Exemple :** `GET /api/composants?type=gpu&q=4070` renvoie
    `[{"id": 5521, "nom": "MSI GeForce RTX 4070 Ventus", "prix": 549}]`.
    """
    type_ = request.args.get("type", "").strip()
    texte = request.args.get("q", "").strip()

    if not type_:
        return jsonify({"erreur": "Le paramètre 'type' est obligatoire."}), 400

    if type_ not in TYPES_VALIDES:
        return jsonify({"erreur": f"Type de composant invalide : '{type_}'."}), 400

    resultats = compatibilite.rechercher(type_, texte)
    return jsonify(resultats), 200