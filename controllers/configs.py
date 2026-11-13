"""Ajout d'une configuration par un utilisateur. Responsable : C1 (tâche 27).

POST /api/configs  {"composants": [412, 2981, 1580, 5521, 801, 330]}
  -> 201 {"id": 57}                        si enregistrée
  -> 400 {"erreur": "raison du refus"}     si refusée
"""
from flask import Blueprint, jsonify, request

from services import configs

bp = Blueprint("configs", __name__, url_prefix="/api")


@bp.post("/configs")
def ajouter():
    data = request.get_json(silent=True) or {}
    try:
        config_id = configs.ajouter(data.get("composants", []))
    except ValueError as e:
        return jsonify({"erreur": str(e)}), 400
    return jsonify({"id": config_id}), 201
