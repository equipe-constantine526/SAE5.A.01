"""Méthode 2 : recommandation par graphe (Personalized PageRank). Responsable : C2 (tâches 29 à 31).

Nœuds = composants, liens = apparaître ensemble dans une config, poids = nombre de configs.
On part des pièces de l'utilisateur, on marche au hasard en suivant plus souvent les liens
lourds, et on revient au départ avec une probabilité de 15 %.
"""
from itertools import combinations

from models.db import execute

PROBA_RETOUR = 0.15


def ajouter_liens(composants_ids):
    """Tâche 29 : +1 sur le poids de chaque paire de la config (6 pièces -> 15 paires)."""
    for a, b in combinations(sorted(composants_ids), 2):
        execute(
            "INSERT INTO lien_graphe (a, b, poids) VALUES (%s, %s, 1) "
            "ON CONFLICT (a, b) DO UPDATE SET poids = lien_graphe.poids + 1",
            (a, b),
        )


def classer(candidats, entree, top=10):
    """Tâche 30 : classe les candidats compatibles selon la marche aléatoire.

    Prototype conseillé : networkx.pagerank(G, alpha=1 - PROBA_RETOUR,
    personalization={id: 1 for id in entree["composants"]}).
    """
    # TODO C2. En attendant : renvoie les candidats sans les classer.
    return [
        {"id": p["id"], "nom": p["nom"], "prix": p.get("prix"), "score": 0.0}
        for p in candidats[:top]
    ]
