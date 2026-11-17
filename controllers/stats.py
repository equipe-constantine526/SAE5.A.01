"""Statistiques pour le dashboard. Responsable : B2 (tâche 21).

GET /api/stats -> [{"methode": "content", "min": .., "max": .., "moyenne": .., "nb": ..}, ...]
"""
from flask import Blueprint, jsonify

from services import mesures

bp = Blueprint("stats", __name__, url_prefix="/api")


@bp.get("/stats")
def stats():
    """Renvoie les temps enregistrés pour les méthodes de recommandation.

    **Reçoit :** aucun paramètre.

    **Renvoie :** une réponse JSON avec le minimum, le maximum, la moyenne et
    le nombre de mesures pour chaque méthode. Par exemple, une mesure de 42,5 ms
    pour `content` apparaît avec `min`, `max` et `moyenne` à 42,5 et `nb` à 1.

    **Exemple :** `GET /api/stats` peut renvoyer
    `[{"methode": "content", "min": 42.5, "max": 42.5, "moyenne": 42.5, "nb": 1}]`.
    """
    return jsonify(mesures.stats())
