"""Recherche de composants pour l'autocomplétion du formulaire. Responsable : A2 (tâche 9).

Un controller ne calcule rien : il lit la requête, appelle un service, renvoie du JSON.
"""
from flask import Blueprint, jsonify, request

from services import compatibilite

bp = Blueprint("composants", __name__, url_prefix="/api")


@bp.get("/composants")
def rechercher():
    """GET /api/composants?type=gpu&q=4070 -> [{"id": .., "nom": .., "prix": ..}]"""
    type_ = request.args.get("type", "")
    texte = request.args.get("q", "")
    resultats = compatibilite.rechercher(type_, texte)
    return jsonify(resultats)
