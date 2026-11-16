"""Tests des règles du score de contenu. Responsable : B1 (tâches 15 à 17).

Les exemples de prix sont synthétiques ; en production, prix et budget sont en
dollars comme dans le catalogue (`models/schema.sql`).
"""

import sys
from types import ModuleType

import pytest

from services.score_contenu import (
    classer,
    composants_selectionnes,
    regle_alim,
    regle_budget,
    regle_equilibre,
    regle_perf_prix,
)


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


def test_regle_equilibre_charge_perf_depuis_le_catalogue(monkeypatch):
    """Vérifie que l'ID envoyé par l'API est remplacé par la fiche catalogue.

    **Reçoit :** un GPU candidat à 75 points et l'identifiant `412` d'un CPU.
    **Renvoie :** aucune valeur ; vérifie que la fiche chargée a `perf=80` et que
    le score obtenu est `0.9375`.
    **Exemple :** `regle_equilibre(gpu_75, {"composants": [412]})` charge le CPU 412.
    """
    requetes = []

    def lire_cpu(sql, parametres):
        requetes.append((sql, parametres))
        return [{"id": 412, "type": "cpu", "perf": 80.0}]

    base_factice = ModuleType("models.db")
    base_factice.query = lire_cpu
    monkeypatch.setitem(sys.modules, "models.db", base_factice)
    entree = {"composants": [412]}

    score = regle_equilibre({"type": "gpu", "perf": 75.0}, entree)

    assert score == pytest.approx(0.9375)
    assert requetes[0][1] == (412,)


def test_composants_selectionnes_charge_chaque_id_separement(monkeypatch):
    """Vérifie le chargement simple d'une fiche catalogue par identifiant.

    **Reçoit :** les identifiants `412` (CPU) et `2981` (carte mère).
    **Renvoie :** les fiches simulées du catalogue, avec leurs types.
    **Exemple :** `[412, 2981]` donne deux dictionnaires correspondant aux deux IDs.
    """
    appels = []

    def lire_fiches(sql, parametres):
        appels.append(parametres)
        if parametres == (412,):
            return [{"id": 412, "type": "cpu", "perf": 80.0}]
        return [{"id": 2981, "type": "carte_mere", "perf": None}]

    base_factice = ModuleType("models.db")
    base_factice.query = lire_fiches
    monkeypatch.setitem(sys.modules, "models.db", base_factice)

    composants = composants_selectionnes({"composants": [412, 2981]})

    assert [piece["type"] for piece in composants] == ["cpu", "carte_mere"]
    assert appels == [(412,), (2981,)]


def test_classement_charge_les_ids_selectionnes_une_seule_fois(monkeypatch):
    """Vérifie que le classement enrichit l'entrée une seule fois depuis le catalogue.

    **Reçoit :** l'ID `412` d'un CPU, un GPU candidat et un budget de 1 200 $.
    **Renvoie :** aucune valeur ; vérifie le score d'équilibre et une seule requête.
    **Exemple :** le CPU chargé à 80 et le GPU candidat à 75 donnent `0.9375`.
    """
    appels = []

    def lire_cpu(sql, parametres):
        appels.append(parametres)
        return [{"id": 412, "type": "cpu", "perf": 80.0}]

    base_factice = ModuleType("models.db")
    base_factice.query = lire_cpu
    monkeypatch.setitem(sys.modules, "models.db", base_factice)
    candidat = {
        "id": 5521,
        "nom": "Fausse RTX",
        "type": "gpu",
        "perf": 75.0,
        "prix": 400,
        "alim_conseillee_w": 550,
    }

    resultats = classer(
        [candidat],
        {"composants": [412], "budget": 1200, "usage": "jeu"},
    )

    assert resultats[0]["detail"]["equilibre"] == pytest.approx(0.9375)
    assert appels == [(412,)]


def test_regle_alim_note_haut_une_marge_conseillee():
    """Vérifie qu'une marge d'alimentation de 100 W reçoit le score maximal.

    **Reçoit :** une « Fausse RTX » conseillée à 550 W et une alimentation de 650 W.
    **Renvoie :** aucune valeur ; vérifie que le score vaut `1.0`.
    **Exemple :** `650 - 550 = 100 W`, dans la zone de 50 à 150 W du guide.
    """
    entree = {
        "composants": [
            {"type": "gpu", "alim_conseillee_w": 550},
        ]
    }
    alimentation = {"type": "alim", "puissance_w": 650}

    assert regle_alim(alimentation, entree) == pytest.approx(1.0)


def test_regle_alim_penalise_marge_trop_faible_ou_trop_grande():
    """Vérifie que les marges hors de la zone du guide sont moins bien notées.

    **Reçoit :** une « Fausse RTX » conseillée à 550 W et des alimentations
    donnant des marges de 25 W et 200 W.
    **Renvoie :** aucune valeur ; vérifie des scores respectifs de `0.5` et `0.75`.
    **Exemple :** `150 / 200 = 0.75` pour la marge de 200 W.
    """
    entree = {"composants": [{"type": "gpu", "alim_conseillee_w": 550}]}

    assert regle_alim({"type": "alim", "puissance_w": 575}, entree) == pytest.approx(0.5)
    assert regle_alim({"type": "alim", "puissance_w": 750}, entree) == pytest.approx(0.75)


def test_regle_alim_note_un_gpu_selon_alimentation_deja_choisie():
    """Vérifie la marge quand la pièce candidate est le GPU.

    **Reçoit :** une « Fausse RTX » conseillée à 550 W et une alimentation choisie
    de 650 W.
    **Renvoie :** aucune valeur ; vérifie que le score vaut `1.0`.
    **Exemple :** `650 - 550 = 100 W`, une marge idéale selon le guide.
    """
    entree = {"composants": [{"type": "alim", "puissance_w": 650}]}
    gpu = {"type": "gpu", "alim_conseillee_w": 550}

    assert regle_alim(gpu, entree) == pytest.approx(1.0)


def test_regle_alim_est_neutre_sans_piece_de_reference():
    """Vérifie qu'une alimentation sans GPU associé reçoit le score neutre.

    **Reçoit :** une alimentation de 650 W et une configuration sans GPU.
    **Renvoie :** aucune valeur ; vérifie que le score vaut `0.5`.
    **Exemple :** sans puissance conseillée de GPU, aucune marge ne peut être calculée.
    """
    entree = {"composants": [{"type": "cpu", "perf": 80}]}

    assert regle_alim({"type": "alim", "puissance_w": 650}, entree) == pytest.approx(0.5)


def test_regle_budget_reserve_quarante_pourcent_au_gpu_en_jeu():
    """Vérifie la part GPU de 40 % pour un usage jeu, donnée dans le guide.

    **Reçoit :** un budget de 1 200 $ et une carte graphique à 480 $ ou 700 $.
    **Renvoie :** aucune valeur ; vérifie les scores `1.0` et `480 / 700`.
    **Exemple :** `1 200 $ × 0.40 = 480 $` pour la carte graphique.
    """
    entree = {"budget": 1200, "usage": "jeu"}

    assert regle_budget({"type": "gpu", "prix": 480}, entree) == pytest.approx(1.0)
    assert regle_budget({"type": "gpu", "prix": 700}, entree) == pytest.approx(480 / 700)


def test_regle_budget_donne_un_score_nul_sans_budget_valide():
    """Vérifie que le score est nul si le budget manque ou n'est pas positif.

    **Reçoit :** une carte graphique à 500 $ et une entrée sans budget valide.
    **Renvoie :** aucune valeur ; vérifie que les scores valent `0.0`.
    **Exemple :** un budget manquant ne permet pas de calculer une part de budget.
    """
    piece = {"type": "gpu", "prix": 500}

    assert regle_budget(piece, {"usage": "jeu"}) == 0.0
    assert regle_budget(piece, {"budget": 0, "usage": "jeu"}) == 0.0
