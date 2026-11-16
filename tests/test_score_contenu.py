"""Tests des règles du score de contenu. Responsable : B1 (tâche 16)."""

import pytest

from services.score_contenu import regle_equilibre


def test_regle_equilibre_note_haut_pour_jeu_equilibre():
    entree = {
        "composants": [
            {"type": "cpu", "perf": 80.0},
            {"type": "gpu", "perf": 75.0},
        ]
    }

    assert regle_equilibre({"type": "gpu", "perf": 75.0}, entree) == pytest.approx(0.9375)


def test_regle_equilibre_est_neutre_sans_cpu_ou_gpu():
    entree = {"composants": [{"type": "ram", "perf": None}]}

    assert regle_equilibre({"type": "ram", "perf": None}, entree) == pytest.approx(0.5)
