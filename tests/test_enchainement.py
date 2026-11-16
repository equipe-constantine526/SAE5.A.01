"""Tests de l'enchaînement pour recommander un PC complet.

Responsable : B2 · Tâche 20
"""

from services import enchainement


def test_recommande_les_types_dans_l_ordre_et_ajoute_les_ids(monkeypatch):
    """Vérifie l'ordre des choix et la config transmise à chaque étape.

    **Reçoit :** une entrée vide avec un budget de 1 200 $ et un usage jeu.
    **Renvoie :** aucune valeur ; vérifie les six types et l'ajout de chaque ID.
    **Exemple :** l'ID du processeur choisi est transmis au filtre de carte mère.
    """
    appels_filtre = []
    composants = []

    for numero, type_piece in enumerate(enchainement.ORDRE_COMPOSANTS, start=101):
        composants.append({"id": numero, "type": type_piece, "nom": type_piece})

    composants_par_type = {}
    for composant in composants:
        composants_par_type[composant["type"]] = composant

    def filtrer(composants_ids, type_piece):
        """Garde une copie des IDs reçus et fournit un candidat de test."""
        appels_filtre.append((composants_ids.copy(), type_piece))
        return [composants_par_type[type_piece]]

    configurations_vues = []

    def classer(candidats, entree_etape):
        """Garde une copie de la config transmise au classement."""
        configurations_vues.append(entree_etape["composants"].copy())
        return candidats

    monkeypatch.setattr(enchainement.compatibilite, "compatibles", filtrer)
    entree = {"composants": [], "budget": 1200, "usage": "jeu"}

    resultat = enchainement.recommander_pc(entree, classer)

    assert [type_piece for _, type_piece in appels_filtre] == list(
        enchainement.ORDRE_COMPOSANTS
    )
    assert [ids for ids, _ in appels_filtre] == [
        [], [101], [101, 102], [101, 102, 103],
        [101, 102, 103, 104], [101, 102, 103, 104, 105],
    ]
    assert configurations_vues == [
        [], [101], [101, 102], [101, 102, 103],
        [101, 102, 103, 104], [101, 102, 103, 104, 105],
    ]
    assert [piece["id"] for piece in resultat["composants"]] == [
        101, 102, 103, 104, 105, 106,
    ]
    assert resultat["type_manquant"] is None
    assert entree["composants"] == []


def test_arrete_et_indique_le_type_sans_candidat(monkeypatch):
    """Vérifie qu'une config partielle signale le premier type sans candidat.

    **Reçoit :** des candidats pour CPU, carte mère et RAM, puis aucun GPU.
    **Renvoie :** aucune valeur ; vérifie les trois pièces et `type_manquant=gpu`.
    **Exemple :** si aucune carte graphique n'est compatible, l'alimentation
    et le boîtier ne sont pas recommandés après le GPU manquant.
    """
    types_appeles = []

    def filtrer(composants_ids, type_piece):
        """Fournit un composant de test, sauf pour le GPU."""
        types_appeles.append(type_piece)
        if type_piece == "gpu":
            return []
        return [{"id": 200 + len(types_appeles), "type": type_piece}]

    def classer(candidats, entree_etape):
        """Renvoie les candidats reçus dans leur ordre initial."""
        return candidats

    monkeypatch.setattr(enchainement.compatibilite, "compatibles", filtrer)
    entree = {"composants": [], "budget": 1200, "usage": "jeu"}

    resultat = enchainement.recommander_pc(entree, classer)

    assert types_appeles == ["cpu", "carte_mere", "ram", "gpu"]
    assert [piece["type"] for piece in resultat["composants"]] == [
        "cpu", "carte_mere", "ram",
    ]
    assert resultat["type_manquant"] == "gpu"
