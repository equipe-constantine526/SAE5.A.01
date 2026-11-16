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
    """Renvoie une note entre 0 et 1 selon l'équilibre CPU/GPU d'une pièce candidate.

    **Reçoit :**
    - `piece` : une pièce candidate, ex. {"id": 501, "type": "gpu", "perf": 75.0}
    - `entree` : la requête utilisateur avec les composants déjà sélectionnés,
      ex. {"composants": [{"type": "cpu", "perf": 80.0}]}

    **Renvoie :** une note proche de 1 quand la pièce est bien équilibrée avec la
    pièce de l'autre type déjà présente, ex. 0.9375 pour un GPU 75 avec un CPU 80.

    **Exemple :** `regle_equilibre({"type": "gpu", "perf": 75.0}, {"composants": [{"type": "cpu", "perf": 80.0}]})`
    renvoie 0.9375.

    **Complexité :** O(c), c = nombre de composants déjà présents dans la config.
    """
    piece_type = piece.get("type")
    piece_perf = piece.get("perf")

    if piece_perf is None:
        return 0.5

    composants = entree.get("composants", [])
    reference = None

    if piece_type == "gpu":
        reference = next((c.get("perf") for c in composants if c.get("type") == "cpu"), None)
    elif piece_type == "cpu":
        reference = next((c.get("perf") for c in composants if c.get("type") == "gpu"), None)

    if reference in (None, 0):
        return 0.5

    # Choix : on compare la performance de la pièce à celle de son complémentaire déjà
    # présent dans la config. Une paire CPU/GPU équilibrée a un ratio proche de 1 ;
    # si l'un des deux est trop loin de l'autre, la note baisse progressivement.
    ratio = piece_perf / reference
    return max(0.0, min(1.0, 1.0 - abs(ratio - 1.0)))


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
