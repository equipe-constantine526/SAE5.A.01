"""Statistiques pour le dashboard. Responsable : B2 (tâche 21).

GET /api/stats -> [{"methode": "content", "min": .., "max": .., "moyenne": ..}, ...]
"""
from flask import Blueprint, jsonify

from services import mesures

bp = Blueprint("stats", __name__, url_prefix="/api")


@bp.get("/stats")
def stats():
    return jsonify(mesures.stats())
