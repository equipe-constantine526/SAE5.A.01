"""Recommande les pièces d'un PC complet dans un ordre fixe.

Responsable : B2 · Tâche 20
"""

from services import compatibilite


ORDRE_COMPOSANTS = ("cpu", "carte_mere", "ram", "gpu", "alim", "boitier")


def recommander_pc(entree, fonction_classement):
    """Choisit les pièces d'un PC complet en ajoutant chaque choix à la config.

    **Reçoit :** `entree`, les préférences utilisateur avec un budget, un usage et
    `composants` (vide pour partir de zéro) ; `fonction_classement`, la fonction qui
    classe les candidats compatibles, par exemple `score_contenu.classer`.

    **Renvoie :** un dictionnaire avec les pièces recommandées et `type_manquant`.
    Cette dernière valeur est `None` si les six types ont été choisis.

    **Exemple :** si le classement choisit d'abord le processeur AMD Ryzen 5 7600,
    son ID est ajouté à la config avant de rechercher une carte mère compatible.

    **Complexité :** O(t × (f + n × c + n log n)), t = 6 types, f = coût du filtre
    à une étape, n = nombre maximal de candidats, c = composants déjà choisis.
    """
    composants_ids = list(entree.get("composants") or [])
    composants_recommandes = []
    type_manquant = None

    # OPTI (P-08) : chaque type lance son propre filtre puis son classement, soit
    # jusqu'à six passages avec des lectures de base répétées. On pourrait regrouper
    # certaines lectures, mais les mesures doivent d'abord montrer un gain utile.
    for type_piece in ORDRE_COMPOSANTS:
        candidats = compatibilite.compatibles(composants_ids, type_piece)
        entree_etape = entree.copy()
        entree_etape["composants"] = composants_ids.copy()
        resultats = fonction_classement(candidats, entree_etape)

        if not resultats:
            # Choix : on renvoie la config partielle et le type manquant plutôt que
            # d'inventer une pièce ou de faire échouer toute la recommandation.
            type_manquant = type_piece
            break

        meilleur = resultats[0]
        composants_recommandes.append(meilleur)
        composants_ids.append(meilleur["id"])

    return {
        "composants": composants_recommandes,
        "type_manquant": type_manquant,
    }
