"""Méthode 2 : recommandation par graphe (Personalized PageRank). Responsable : C2 (tâches 29 à 31).

Nœuds = composants, liens = apparaître ensemble dans une config, poids = nombre de configs.
On part des pièces de l'utilisateur, on marche au hasard en suivant plus souvent les liens
lourds, et on revient au départ avec une probabilité de 15 %.
"""
from itertools import combinations

import networkx as nx

from models.db import get_connection, query

PROBA_RETOUR = 0.15
_graphe = None  # cache en mémoire, reconstruit quand un lien est ajouté


def ajouter_liens(composants_ids):
    """Tâche 29 : +1 sur le poids de chaque paire de la config (6 pièces -> 15 paires).

    Une seule connexion pour toutes les paires : plus rapide, et tout ou rien en cas d'erreur.
    """
    global _graphe
    # set() évite une paire (a, a) si un id apparaît deux fois ; sorted garantit a < b
    paires = list(combinations(sorted(set(composants_ids)), 2))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO lien_graphe (a, b, poids) VALUES (%s, %s, 1) "
                "ON CONFLICT (a, b) DO UPDATE SET poids = lien_graphe.poids + 1",
                paires,
            )
    _graphe = None  # le cache est périmé, il sera reconstruit à la prochaine requête


def _get_graphe():
    """Charge le graphe depuis lien_graphe une seule fois, puis le garde en mémoire."""
    global _graphe
    if _graphe is None:
        g = nx.Graph()
        for ligne in query("SELECT a, b, poids FROM lien_graphe"):
            g.add_edge(ligne["a"], ligne["b"], poids=ligne["poids"])
        _graphe = g
    return _graphe


def classer(candidats, entree, top=10):
    """Tâche 30 : classe les candidats compatibles par Personalized PageRank.

    alpha = 1 - PROBA_RETOUR : dans networkx, alpha est la probabilité de suivre un lien,
    donc 0,85 correspond à 15 % de retour au départ.
    Les scores sont ramenés entre 0 et 1 (le meilleur vaut 1), comme la méthode 1,
    pour que le dashboard puisse comparer les deux.
    """
    g = _get_graphe()
    # personalization plante si un id est absent du graphe, d'où le filtre
    depart = {i: 1 for i in entree["composants"] if i in g}
    if not depart:
        return []  # démarrage à froid : aucune pièce de l'utilisateur dans le graphe

    scores = nx.pagerank(
        g, alpha=1 - PROBA_RETOUR, personalization=depart, weight="poids"
    )
    notes = [(p, scores.get(p["id"], 0.0)) for p in candidats]
    notes = [(p, s) for p, s in notes if s > 0]
    if not notes:
        return []

    notes.sort(key=lambda x: x[1], reverse=True)
    meilleur = notes[0][1]
    return [
        {"id": p["id"], "nom": p["nom"], "prix": p.get("prix"), "score": s / meilleur}
        for p, s in notes[:top]
    ]