"""Chronométrage des recommandations. Responsable : B2 (tâche 21)."""
from models.db import execute, query


def enregistrer(methode, temps_ms):
    try:
        execute("INSERT INTO mesure (methode, temps_ms) VALUES (%s, %s)", (methode, temps_ms))
    except Exception:
        pass  # une mesure ratée ne doit jamais casser une recommandation


def stats():
    return query(
        "SELECT methode, MIN(temps_ms) AS min, MAX(temps_ms) AS max, "
        "ROUND(AVG(temps_ms), 2) AS moyenne, COUNT(*) AS nb "
        "FROM mesure GROUP BY methode"
    )
