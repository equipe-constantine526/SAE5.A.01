"""Classe les pièces compatibles selon leurs caractéristiques et l'usage demandé.

Responsable : B1 · Tâches 15 à 18
"""

import math

POIDS = {
    "jeu":       {"perf_prix": 0.4, "equilibre": 0.3, "alim": 0.1, "budget": 0.2},
    "montage":   {"perf_prix": 0.3, "equilibre": 0.3, "alim": 0.1, "budget": 0.3},
    "bureautique": {"perf_prix": 0.3, "equilibre": 0.1, "alim": 0.1, "budget": 0.5},
}


def ratio_perf_prix(piece):
    """Calcule la performance par dollar, ou zéro si les données sont inutilisables.

    **Reçoit :** `piece`, une fiche de composant avec `perf` et `prix`,
    par exemple `{"nom": "MSI GeForce RTX 4070 Ventus", "perf": 29.15, "prix": 549}`.

    **Renvoie :** un nombre positif ou `0.0` si la performance ou le prix manque,
    si le prix n'est pas positif, ou si une valeur n'est pas finie.

    **Exemple :** avec les valeurs illustratives du guide pour la MSI GeForce RTX 4070
    Ventus, `29.15 / 549` donne environ `0.053` point par dollar.

    **Complexité :** O(1).
    """
    try:
        performance = float(piece.get("perf"))
        prix = float(piece.get("prix"))
    except (TypeError, ValueError):
        return 0.0

    # Choix : une fiche incomplète reçoit zéro plutôt que de faire échouer toute
    # la recommandation ; sans prix positif et fini, son rapport n'est pas exploitable.
    if not math.isfinite(performance) or not math.isfinite(prix):
        return 0.0
    if performance < 0 or prix <= 0:
        return 0.0

    return performance / prix


def normaliser_perf_prix(candidats):
    """Renvoie les rapports performance/prix normalisés dans l'ordre des candidats.

    **Reçoit :** les fiches des pièces compatibles, par exemple une liste contenant
    la MSI GeForce RTX 4070 Ventus (`perf=29.15`, `prix=549` dans l'exemple du guide).

    **Renvoie :** une liste de scores entre 0 et 1, dans le même ordre que `candidats`.
    Le meilleur rapport reçoit 1.0. Si aucun rapport n'est valide, tous les scores
    valent `0.0`.

    **Exemple :** si cette carte est seule candidate, son score normalisé est `[1.0]`.

    **Complexité :** O(n), n = nombre de candidats.
    """
    ratios = []
    for piece in candidats:
        ratios.append(ratio_perf_prix(piece))

    # OPTI (P-07) : on relit tous les candidats pour normaliser chaque demande.
    # Une normalisation globale calculée à l'import éviterait ce parcours, mais
    # changerait le score relatif aux pièces compatibles de la demande.
    meilleur_ratio = max(ratios, default=0.0)
    if meilleur_ratio == 0:
        return [0.0 for _ in ratios]

    scores = []
    for ratio in ratios:
        scores.append(ratio / meilleur_ratio)
    return scores


def regle_perf_prix(piece, candidats):
    """Note le rapport performance/prix d'une pièce parmi les pièces compatibles.

    **Reçoit :** `piece`, la fiche à noter, et `candidats`, les fiches compatibles.
    Exemple : la MSI GeForce RTX 4070 Ventus avec `perf=29.15` et `prix=549`, parmi
    les cartes graphiques compatibles (valeurs illustratives reprises du guide).

    **Renvoie :** un score compris entre 0 et 1. Le meilleur rapport vaut 1.

    **Exemple :** si cette carte détient le meilleur rapport de la liste, elle reçoit `1.0`.

    **Complexité :** O(n), n = nombre de candidats.
    """
    meilleur_ratio = 0.0
    for candidat in candidats:
        meilleur_ratio = max(meilleur_ratio, ratio_perf_prix(candidat))

    if meilleur_ratio == 0:
        return 0.0
    return ratio_perf_prix(piece) / meilleur_ratio


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
    """Classe les candidats selon les règles et les poids liés à l'usage.

    **Reçoit :** `candidats`, les composants compatibles ; `entree`, les préférences
    de l'utilisateur, dont `usage` ; `top`, le nombre maximum de résultats.
    Exemple : une liste de cartes graphiques compatibles contenant la MSI GeForce RTX
    4070 Ventus, et `{"usage": "jeu"}`.

    **Renvoie :** au plus `top` dictionnaires triés par score décroissant, avec le
    score total et le détail des règles. Une RTX 4070 peut ainsi apparaître avec
    son prix, son score et son score `perf_prix`.

    **Complexité :** O(n log n), n = nombre de candidats, à cause du tri final.
    """
    poids = POIDS.get(entree["usage"], POIDS["jeu"])
    resultats = []
    scores_perf_prix = normaliser_perf_prix(candidats)
    for index, piece in enumerate(candidats):
        detail = {
            "perf_prix": scores_perf_prix[index],
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
