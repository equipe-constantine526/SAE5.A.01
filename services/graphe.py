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
    """Tâche 29 : ajoute 1 au poids du lien de chaque paire de pièces d'une config.

    **Reçoit :**
    - `composants_ids` : ids des pièces de la config, ex. `[412, 2981, 5521]`
      (un Ryzen 5 7600, une MSI B650 Tomahawk, une RTX 4070)

    **Renvoie :** rien. La table `lien_graphe` est mise à jour.

    **Exemple :** `ajouter_liens([2981, 412, 5521])` ajoute 1 aux liens (412, 2981),
    (412, 5521) et (2981, 5521). Avec 6 pièces, ça fait 15 paires.

    **Complexité :** O(k²), k = nombre de pièces de la config (k × (k-1) / 2 paires).
    """
    global _graphe

    # Choix : on range chaque paire avec le plus petit id en premier (a < b). Sans ça, la
    # paire (412, 1580) pourrait être stockée aussi en (1580, 412) : deux lignes pour un
    # même lien, avec chacune la moitié du poids. La table l'impose aussi (CHECK a < b).
    # set() enlève les ids en double : sans lui, un id répété donnerait la paire (a, a),
    # que la table refuse.
    paires = list(combinations(sorted(set(composants_ids)), 2))
    if not paires:
        return  # une seule pièce : aucun lien à ajouter

    # Choix : une seule connexion pour toutes les paires (get_connection) plutôt qu'un
    # appel à execute() par paire. Les paires d'une config forment un tout : si l'une
    # échoue, la transaction est annulée et aucun poids n'est modifié. Alternative écartée :
    # 15 appels à execute() = 15 transactions, donc des liens à moitié ajoutés en cas d'erreur.
    # OPTI (P-05) : ouverture de la connexion
    #   Maintenant : une connexion PostgreSQL ouverte puis fermée à chaque ajout de config.
    #   Pourquoi c'est améliorable : le coût d'ouverture est payé à chaque ajout.
    #   Piste : un pool de connexions réutilisées (psycopg_pool).
    #   Gain attendu : à mesurer (temps de POST /api/configs avant et après).
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Si le lien existe déjà (la paire apparaît dans une autre config), on ajoute 1
            # à son poids au lieu de créer un doublon : le poids compte les configs.
            cur.executemany(
                "INSERT INTO lien_graphe (a, b, poids) VALUES (%s, %s, 1) "
                "ON CONFLICT (a, b) DO UPDATE SET poids = lien_graphe.poids + 1",
                paires,
            )

    # OPTI (P-11) : graphe en mémoire jeté après chaque ajout
    #   Maintenant : le graphe en mémoire est supprimé, puis relu en entier depuis
    #                lien_graphe à la prochaine recommandation. Complexité O(l), l = nombre
    #                de liens du graphe, pour ajouter seulement k × (k-1) / 2 paires.
    #   Pourquoi c'est améliorable : on relit tous les liens pour en avoir ajouté 15.
    #   Piste : ajouter directement ces paires au graphe en mémoire.
    #   Gain attendu : à mesurer (temps de la première recommandation après un ajout).
    _graphe = None


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