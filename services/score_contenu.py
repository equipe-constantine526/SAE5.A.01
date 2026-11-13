"""Méthode 1 : score sur les fiches techniques. Responsable : B1 (tâches 15 à 18).

score = w1 * perf_prix + w2 * equilibre + w3 * alim + w4 * budget
Chaque règle renvoie une note entre 0 et 1.
Les poids sont NOS choix : notez pourquoi dans le rapport, on vous le demandera à l'oral.
"""

POIDS = {
    "jeu":       {"perf_prix": 0.4, "equilibre": 0.3, "alim": 0.1, "budget": 0.2},
    "montage":   {"perf_prix": 0.3, "equilibre": 0.3, "alim": 0.1, "budget": 0.3},
    "bureautique": {"perf_prix": 0.3, "equilibre": 0.1, "alim": 0.1, "budget": 0.5},
}


def regle_perf_prix(piece, candidats):
    # TODO B1 (tâche 15) : perf / prix, ramené entre 0 et 1 parmi les candidats
    return 0.0


def regle_equilibre(piece, entree):
    # TODO B1 (tâche 16)
    return 0.0


def regle_alim(piece, entree):
    # TODO B1 (tâche 17)
    return 0.0


def regle_budget(piece, entree):
    # TODO B1 (tâche 17)
    return 0.0


def classer(candidats, entree, top=10):
    """Note chaque candidat et renvoie les `top` meilleurs, avec le détail du score (tâche 23)."""
    poids = POIDS.get(entree["usage"], POIDS["jeu"])
    resultats = []
    for piece in candidats:
        detail = {
            "perf_prix": regle_perf_prix(piece, candidats),
            "equilibre": regle_equilibre(piece, entree),
            "alim": regle_alim(piece, entree),
            "budget": regle_budget(piece, entree),
        }
        score = sum(poids[k] * v for k, v in detail.items())
        resultats.append({
            "id": piece["id"], "nom": piece["nom"], "prix": piece.get("prix"),
            "score": round(score, 3), "detail": detail,
        })
    resultats.sort(key=lambda r: r["score"], reverse=True)
    return resultats[:top]
