"""Ajout d'une configuration utilisateur. Responsable : C1 (tâche 26).

Étapes : ids existants -> config compatible -> pas un doublon -> enregistrer -> mettre à jour le graphe.
Lève ValueError("raison") en cas de refus : le controller la transforme en erreur 400.
"""
from services import compatibilite, graphe


def ajouter(composants_ids):
    if not composants_ids:
        raise ValueError("aucun composant fourni")

    ok, raison = compatibilite.config_valide(composants_ids)
    if not ok:
        raise ValueError(raison)

    # TODO C1 : vérifier que chaque id existe, refuser les doublons,
    #           INSERT dans configuration + configuration_composant (origine='utilisateur', validee=FALSE)
    config_id = None

    graphe.ajouter_liens(composants_ids)
    return config_id
