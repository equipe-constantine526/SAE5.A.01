"""Tests de la règle performance/prix. Responsable : B1 (tâche 15).

Les valeurs des pièces A et B reprennent l'exemple de calcul du guide ;
ce ne sont pas des composants réels du catalogue.
"""

import pytest

from services.score_contenu import classer, regle_perf_prix


PIECE_A = {"id": 1, "nom": "Pièce A", "perf": 70, "prix": 500}
PIECE_B = {"id": 2, "nom": "Pièce B", "perf": 90, "prix": 900}


def test_meilleur_rapport_performance_prix_vaut_un():
    """Vérifie que le meilleur rapport reçoit 1.

    **Reçoit :** les deux pièces illustratives du guide : A (`perf=70`, `prix=500 $`)
    et B (`perf=90`, `prix=900 $`).
    **Renvoie :** aucune valeur ; vérifie que le score de A vaut `1.0`.
    **Exemple :** `70 / 500 = 0.14`, le meilleur rapport, donc score `1.0`.
    """
    candidats = [PIECE_A, PIECE_B]

    score = regle_perf_prix(PIECE_A, candidats)

    assert score == pytest.approx(1.0)


def test_rapport_moins_efficace_est_normalise_par_le_meilleur():
    """Vérifie que le rapport de B est ramené à l'échelle du meilleur.

    **Reçoit :** A (`perf=70`, `prix=500 $`) et B (`perf=90`, `prix=900 $`).
    **Renvoie :** aucune valeur ; vérifie que le score de B vaut environ `0.71`.
    **Exemple :** le rapport de B (`0.10`) divisé par celui de A (`0.14`) vaut `0.71`.
    """
    candidats = [PIECE_A, PIECE_B]

    score = regle_perf_prix(PIECE_B, candidats)

    assert score == pytest.approx(0.10 / 0.14)


def test_prix_manquant_ou_nul_donne_un_score_nul():
    """Vérifie le résultat lorsque le prix nécessaire au calcul n'est pas valide.

    **Reçoit :** deux fiches illustratives, l'une sans prix et l'autre avec un prix nul.
    **Renvoie :** aucune valeur ; vérifie que chaque score est `0.0`.
    **Exemple :** une carte graphique de performance 70 sans prix reçoit `0.0`.
    """
    candidats = [
        {"id": 3, "nom": "Sans prix", "perf": 70},
        {"id": 4, "nom": "Prix nul", "perf": 70, "prix": 0},
    ]

    assert regle_perf_prix(candidats[0], candidats) == 0.0
    assert regle_perf_prix(candidats[1], candidats) == 0.0


def test_absence_de_candidats_donne_un_score_nul():
    """Vérifie le comportement quand aucune pièce compatible n'est proposée.

    **Reçoit :** la fiche illustrative de A et une liste de candidats vide.
    **Renvoie :** aucune valeur ; vérifie que le score vaut `0.0`.
    **Exemple :** `regle_perf_prix(PIECE_A, [])` vaut `0.0`.
    """
    assert regle_perf_prix(PIECE_A, []) == 0.0


def test_classement_place_le_meilleur_rapport_en_premier():
    """Vérifie que le classement utilise la règle performance/prix de la tâche 15.

    **Reçoit :** les pièces illustratives A et B et l'usage `jeu`.
    **Renvoie :** aucune valeur ; vérifie que A est classée avant B avec le score `1.0`.
    **Exemple :** `classer([PIECE_B, PIECE_A], {"usage": "jeu"})` place A en tête.
    """
    resultats = classer([PIECE_B, PIECE_A], {"usage": "jeu"})

    assert resultats[0]["id"] == PIECE_A["id"]
    assert resultats[0]["detail"]["perf_prix"] == pytest.approx(1.0)
    assert resultats[1]["detail"]["perf_prix"] == pytest.approx(0.10 / 0.14)
