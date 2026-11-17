"""Chronométrage des recommandations. Responsable : B2 (tâche 21)."""
from models.db import execute, query


def enregistrer(methode, temps_ms):
    """Enregistre le temps d'une recommandation en base.

    **Reçoit :** `methode`, `"content"` ou `"graph"`, et `temps_ms`, le temps en
    millisecondes, par exemple `42.5`.

    **Renvoie :** rien. Si l'enregistrement échoue, la recommandation continue
    quand même.

    **Exemple :** `enregistrer("content", 42.5)` ajoute une mesure de 42,5 ms.
    """
    try:
        execute("INSERT INTO mesure (methode, temps_ms) VALUES (%s, %s)", (methode, temps_ms))
    except Exception:
        # Choix : on ignore une erreur de mesure plutôt que de faire échouer la
        # recommandation ; afficher les résultats reste prioritaire pour l'utilisateur.
        pass


def stats():
    """Calcule les statistiques de temps pour chaque méthode.

    **Reçoit :** rien.

    **Renvoie :** une liste contenant, pour chaque méthode, les temps minimum,
    maximum et moyen, ainsi que le nombre de mesures. Par exemple, une mesure
    de 42,5 ms pour `content` apparaît avec `min`, `max` et `moyenne` à 42,5.

    **Exemple :** `stats()` peut renvoyer `[{"methode": "content", "min": 42.5,
    "max": 42.5, "moyenne": 42.5, "nb": 1}]`.
    """
    return query(
        "SELECT methode, MIN(temps_ms) AS min, MAX(temps_ms) AS max, "
        "ROUND(AVG(temps_ms), 2) AS moyenne, COUNT(*) AS nb "
        "FROM mesure GROUP BY methode"
    )
