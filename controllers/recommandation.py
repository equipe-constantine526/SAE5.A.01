"""Les deux routes de recommandation. Responsables : B2 (content, tâche 19), C2 (graph, tâche 31).

Les DEUX routes ont exactement le même format d'entrée et de sortie (contrat d'API),
sinon le dashboard ne peut pas comparer les méthodes.

Entrée : {"composants": [412, 2981], "budget": 1200, "usage": "jeu", "type_cherche": "gpu"}
Sortie : {"resultats": [{"id": .., "nom": .., "prix": .., "score": ..}], "temps_ms": 42}
"""
import time

from flask import Blueprint, jsonify, request

from services import compatibilite, graphe, mesures, score_contenu

bp = Blueprint("recommandation", __name__, url_prefix="/api/recommend")


def _lire_entree():
    data = request.get_json(silent=True) or {}
    return {
        "composants": data.get("composants", []),
        "budget": data.get("budget"),
        "usage": data.get("usage", "jeu"),
        "type_cherche": data.get("type_cherche"),
    }


def _recommander(methode, classer):
    entree = _lire_entree()
    debut = time.perf_counter()

    candidats = compatibilite.compatibles(entree["composants"], entree["type_cherche"])
    resultats = classer(candidats, entree)

    temps_ms = round((time.perf_counter() - debut) * 1000, 2)
    mesures.enregistrer(methode, temps_ms)
    return jsonify({"resultats": resultats, "temps_ms": temps_ms})


@bp.post("/content")
def content():
    """Méthode 1 : score sur les fiches techniques."""
    return _recommander("content", score_contenu.classer)


@bp.post("/graph")
def graph():
    """Méthode 2 : Personalized PageRank sur le graphe des configs."""
    return _recommander("graph", graphe.classer)
