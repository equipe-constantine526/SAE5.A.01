"""Tests des règles du score de contenu. Responsable : B1 (tâches 15 et 16)."""

import pytest

from services.score_contenu import classer, regle_equilibre, regle_perf_prix


PIECE_A = {"id": 1, "nom": "Pièce A", "perf": 70, "prix": 500}
PIECE_B = {"id": 2, "nom": "Pièce B", "perf": 90, "prix": 900}


def test_meilleur_rapport_performance_prix_vaut_un():
    """Vérifie que le meilleur rapport reçoit 1."""
    candidats = [PIECE_A, PIECE_B]

    score = regle_perf_prix(PIECE_A, candidats)

    assert score == pytest.approx(1.0)


def test_rapport_moins_efficace_est_normalise_par_le_meilleur():
    """Vérifie que le rapport de B est ramené à l'échelle du meilleur."""
    candidats = [PIECE_A, PIECE_B]

    score = regle_perf_prix(PIECE_B, candidats)

    assert score == pytest.approx(0.10 / 0.14)


def test_prix_manquant_ou_nul_donne_un_score_nul():
    """Vérifie le résultat quand le prix n'est pas exploitable."""
    candidats = [
        {"id": 3, "nom": "Sans prix", "perf": 70},
        {"id": 4, "nom": "Prix nul", "perf": 70, "prix": 0},
    ]

    assert regle_perf_prix(candidats[0], candidats) == 0.0
    assert regle_perf_prix(candidats[1], candidats) == 0.0


def test_absence_de_candidats_donne_un_score_nul():
    """Vérifie le comportement sans candidat."""
    assert regle_perf_prix(PIECE_A, []) == 0.0


def test_classement_place_le_meilleur_rapport_en_premier():
    """Vérifie que le classement utilise la règle performance/prix."""
    resultats = classer([PIECE_B, PIECE_A], {"usage": "jeu"})

    assert resultats[0]["id"] == PIECE_A["id"]
    assert resultats[0]["detail"]["perf_prix"] == pytest.approx(1.0)
    assert resultats[1]["detail"]["perf_prix"] == pytest.approx(0.10 / 0.14)


def test_regle_equilibre_note_haut_pour_jeu_equilibre():
    """Vérifie qu'un GPU proche du CPU reçoit une note élevée."""
    entree = {
        "composants": [
            {"type": "cpu", "perf": 80.0},
            {"type": "gpu", "perf": 75.0},
        ]
    }

    assert regle_equilibre({"type": "gpu", "perf": 75.0}, entree) == pytest.approx(0.9375)


def test_regle_equilibre_est_neutre_sans_cpu_ou_gpu():
    """Vérifie qu'un composant hors paire CPU/GPU reste neutre."""
    entree = {"composants": [{"type": "ram", "perf": None}]}

    assert regle_equilibre({"type": "ram", "perf": None}, entree) == pytest.approx(0.5)
