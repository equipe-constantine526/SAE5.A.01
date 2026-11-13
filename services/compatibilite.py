"""Filtre de compatibilité, partagé par les deux méthodes. Responsable : A2 (tâche 8).

Règles à coder :
  - socket du processeur == socket de la carte mère
  - type de RAM == type accepté par la carte mère
  - puissance de l'alim >= alim conseillée de la carte graphique
  - format de la carte mère accepté par le boîtier
"""
from models.db import query


def compatibles(composants_ids, type_cherche):
    """Renvoie les pièces de type `type_cherche` compatibles avec `composants_ids`.

    Exemple : compatibles([412], "carte_mere") avec 412 = un CPU AM5
              -> toutes les cartes mères AM5.
    """
    # TODO A2 : appliquer les règles ci-dessus.
    # En attendant : toutes les pièces du type demandé, sans filtre.
    return query(
        "SELECT * FROM composant WHERE type = %s LIMIT 200",
        (type_cherche,),
    )


def config_valide(composants_ids):
    """Renvoie (True, None) si la config complète est compatible, sinon (False, "raison").
    Utilisée par l'ajout de config (C1, tâche 26)."""
    # TODO A2
    return True, None


def rechercher(type_, texte):
    """Recherche pour l'autocomplétion (tâche 9). 20 résultats max."""
    return query(
        "SELECT id, nom, prix FROM composant WHERE type = %s AND nom ILIKE %s ORDER BY nom LIMIT 20",
        (type_, f"%{texte}%"),
    )
