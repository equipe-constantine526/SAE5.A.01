"""Classe les pièces compatibles selon leurs caractéristiques et l'usage demandé.

Responsable : B1 · Tâches 15 à 18
"""

import math

# Choix : les poids sont des priorités choisies pour le projet, pas des valeurs
# mesurées. En jeu, on met l'accent sur le rapport perf/prix et l'équilibre ; en
# montage, le budget pèse davantage, tandis que l'équilibre favorise déjà le CPU
# dans sa propre règle. En bureautique, le budget devient prioritaire car le besoin
# de performance est plus limité. L'alimentation garde 10 % partout : la compatibilité
# vérifie déjà qu'elle est suffisante. Chaque ligne totalise 1 pour garder le score
# final entre 0 et 1.
POIDS = {
    "jeu":       {"perf_prix": 0.4, "equilibre": 0.3, "alim": 0.1, "budget": 0.2},
    "montage":   {"perf_prix": 0.3, "equilibre": 0.3, "alim": 0.1, "budget": 0.3},
    "bureautique": {"perf_prix": 0.3, "equilibre": 0.1, "alim": 0.1, "budget": 0.5},
}

# Le guide ne fixe qu'une part précise : 40 % du budget pour le GPU en jeu.
# Les autres couples usage/type utilisent le budget entier jusqu'à décision de l'équipe.
PART_BUDGET_PAR_USAGE = {"jeu": {"gpu": 0.4}}


def ratio_perf_prix(piece):
    """Calcule la performance par dollar, ou zéro si les données sont inutilisables.

    **Reçoit :** `piece`, une fiche de composant du catalogue avec `perf` et `prix`,
    par exemple `{"type": "gpu", "perf": 80, "prix": 549}`.

    **Renvoie :** un nombre positif ou `0.0` si la performance ou le prix manque,
    si le prix n'est pas positif, ou si une valeur n'est pas finie.

    **Exemple :** pour une fiche de catalogue avec `perf=80` et `prix=549`, le rapport
    est `80 / 549`, soit environ `0.146` point d'indice par dollar.

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
    une carte graphique avec `perf=80` et `prix=549` (valeurs d'exemple).

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
    Exemple : une carte graphique avec `perf=80` et `prix=549`, parmi les cartes
    graphiques compatibles (valeurs d'exemple).

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


def composants_selectionnes(entree):
    """Charge les fiches catalogue des composants déjà choisis.

    **Reçoit :** `entree` avec `composants`, une liste d'identifiants envoyés par
    l'API ou de fiches déjà chargées, par exemple `[412]` ou
    `[{"id": 412, "type": "cpu"}]`.

    **Renvoie :** les fiches avec les champs du catalogue utilisés par les règles,
    notamment `id`, `type`, `perf`, `alim_conseillee_w` et `puissance_w`.

    **Exemple :** l'identifiant `[412]` devient la fiche du processeur 412 avec son
    type et son indice de performance.

    **Complexité :** O(c), c = nombre de composants sélectionnés, plus une requête
    SQL par identifiant qui n'a pas déjà sa fiche.
    """
    composants = entree.get("composants") or []
    fiches = []
    identifiants = []

    for composant in composants:
        if isinstance(composant, dict):
            fiches.append(composant)
        else:
            identifiants.append(composant)

    if identifiants:
        from models.db import query

        # OPTI (P-02) : on lit maintenant chaque composant sélectionné avec une
        # requête SQL séparée. Une requête groupée avec WHERE id = ANY(%s) éviterait
        # ces allers-retours ; on garde cette version simple comme référence avant
        # mesure de l'optimisation.
        for identifiant in identifiants:
            fiches_catalogue = query(
                """SELECT id, type, perf, alim_conseillee_w, puissance_w
                   FROM composant WHERE id = %s""",
                (identifiant,),
            )
            if fiches_catalogue:
                fiches.append(fiches_catalogue[0])

    return fiches


def regle_equilibre(piece, entree):
    """Note l'équilibre CPU/GPU selon l'usage et l'indice catalogue `perf`.

    **Reçoit :**
    - `piece` : une pièce candidate, ex. {"id": 501, "type": "gpu", "perf": 75.0}
    - `entree` : la requête utilisateur avec les composants déjà sélectionnés,
      sous forme d'identifiants ou de fiches, ex. {"composants": [412]}.

    **Renvoie :** une note entre 0 et 1. Un écart reste pénalisé, mais moins quand
    le composant le plus performant correspond à l'usage : GPU pour le jeu, CPU
    pour le montage vidéo.

    **Exemple :** avec un CPU à 40 et un GPU à 95, l'écart vaut `(95 - 40) / 100`,
    soit `0.55`. La note est `0.725` en jeu et `0.45` en montage vidéo.

    **Complexité :** O(c), c = composants déjà présents, plus une requête SQL par
    identifiant si l'entrée contient des identifiants.
    """
    piece_type = piece.get("type")
    piece_perf = piece.get("perf")

    if piece_perf is None:
        return 0.5

    composants = composants_selectionnes(entree)
    reference = None

    if piece_type == "gpu":
        reference = next((c.get("perf") for c in composants if c.get("type") == "cpu"), None)
    elif piece_type == "cpu":
        reference = next((c.get("perf") for c in composants if c.get("type") == "gpu"), None)

    if reference in (None, 0):
        return 0.5

    if piece_type == "gpu":
        performance_gpu = piece_perf
        performance_cpu = reference
    else:
        performance_gpu = reference
        performance_cpu = piece_perf

    ecart = (performance_gpu - performance_cpu) / 100
    usage = entree.get("usage", "jeu")
    gpu_plus_performant = ecart > 0

    # Choix : le guide indique quel composant peut être plus performant selon
    # l'usage, mais ne donne pas de formule. On garde une pénalité pour l'écart
    # (exemple CPU 40/GPU 95), réduite de moitié dans le sens favorisé par l'usage.
    if usage == "jeu" and gpu_plus_performant:
        coefficient_penalite = 0.5
    elif usage == "montage" and not gpu_plus_performant:
        coefficient_penalite = 0.5
    else:
        coefficient_penalite = 1.0

    penalite = abs(ecart) * coefficient_penalite
    return max(0.0, 1.0 - penalite)


def regle_alim(piece, entree):
    """Note la marge entre la puissance d'alimentation et la puissance conseillée.

    **Reçoit :** `piece`, une alimentation candidate ou un GPU candidat ; `entree`,
    avec les composants déjà choisis. Exemple : une alimentation de 650 W et une
    « Fausse RTX » nécessitant 550 W.

    **Renvoie :** une note entre 0 et 1. Une marge de 50 à 150 W vaut 1 ; une marge
    négative vaut 0. Renvoie 0.5 si la pièce ou sa puissance de référence manque.

    **Exemple :** 650 W face à 550 W donne une marge de 100 W et un score de `1.0`.

    **Complexité :** O(c), c = composants déjà choisis, plus une requête SQL par
    identifiant si l'entrée contient des identifiants.
    """
    composants = composants_selectionnes(entree)
    type_piece = piece.get("type")
    puissance_alim = None
    puissance_conseillee = None

    if type_piece == "alim":
        puissance_alim = piece.get("puissance_w")
        for composant in composants:
            if composant.get("type") == "gpu":
                puissance_conseillee = composant.get("alim_conseillee_w")
                break
    elif type_piece == "gpu":
        puissance_conseillee = piece.get("alim_conseillee_w")
        for composant in composants:
            if composant.get("type") == "alim":
                puissance_alim = composant.get("puissance_w")
                break
    else:
        return 0.5

    try:
        puissance_alim = float(puissance_alim)
        puissance_conseillee = float(puissance_conseillee)
    except (TypeError, ValueError):
        return 0.5

    if not math.isfinite(puissance_alim) or not math.isfinite(puissance_conseillee):
        return 0.5
    if puissance_alim <= 0 or puissance_conseillee <= 0:
        return 0.5

    marge = puissance_alim - puissance_conseillee
    if marge < 0:
        return 0.0

    # Choix : le guide donne une zone idéale de 50 à 150 W, sans formule exacte.
    # On augmente linéairement jusqu'à 50 W puis on baisse comme 150 / marge au-delà.
    if marge < 50:
        return marge / 50
    if marge <= 150:
        return 1.0
    return 150 / marge


def regle_budget(piece, entree):
    """Note le prix d'une pièce par rapport à la part prévue du budget.

    **Reçoit :** `piece`, une fiche avec `type` et `prix` ; `entree`, contenant
    `budget` en dollars et `usage`. Le catalogue stocke `prix` en dollars.

    **Renvoie :** une note entre 0 et 1. Pour un CPU ou un GPU, le score vaut 1
    sous la part prévue et diminue si elle est dépassée. Pour la RAM, les cartes
    mères, les alimentations et les boîtiers, il baisse avec le prix afin de
    départager ces pièces sans indice de performance. Les parts non précisées par
    le guide utilisent le budget entier, sans inventer de pourcentage.

    **Exemple :** avec un budget de 1 200 $ et un GPU à 700 $, la part de 40 % vaut
    480 $ ; le score vaut `480 / 700`, soit environ `0.686`. Une carte mère à 120 $
    sans indice `perf` reçoit `1200 / (1200 + 120)`, soit environ `0.909`.

    **Complexité :** O(1).
    """
    try:
        prix = float(piece.get("prix"))
        budget = float(entree.get("budget"))
    except (TypeError, ValueError):
        return 0.0

    # Choix : si le prix ou le budget manque, le score vaut zéro car on ne peut pas
    # vérifier que la pièce respecte la limite prévue.
    if not math.isfinite(prix) or not math.isfinite(budget):
        return 0.0
    if prix < 0 or budget <= 0:
        return 0.0

    usage = entree.get("usage", "jeu")
    type_piece = piece.get("type")
    part = PART_BUDGET_PAR_USAGE.get(usage, {}).get(type_piece, 1.0)
    budget_piece = budget * part

    if type_piece not in {"cpu", "gpu"}:
        # Choix : sans perf ni caractéristiques détaillées, favoriser une pièce
        # moins chère donne un ordre explicable au lieu d'une égalité arbitraire.
        # Pour la RAM, cela reste approximatif tant que capacité et vitesse manquent.
        return budget_piece / (budget_piece + prix)

    if prix <= budget_piece:
        return 1.0
    return budget_piece / prix


def obtenir_score(resultat):
    """Renvoie le score d'un résultat pour le tri des recommandations.

    **Reçoit :** un dictionnaire de résultat, par exemple `{"nom": "RTX 4070",
    "score": 0.87}`.

    **Renvoie :** le score numérique du résultat, ici `0.87`.

    **Exemple :** `obtenir_score({"score": 0.87})` renvoie `0.87`.

    **Complexité :** O(1).
    """
    return resultat["score"]


def diversifier_resultats(resultats, top):
    """Garde le meilleur modèle de chaque chipset ou famille dans la liste.

    **Reçoit :** les résultats déjà triés par score et le nombre maximal demandé.
    **Renvoie :** au plus `top` résultats, avec un seul élément par chipset ou famille.
    **Exemple :** parmi plusieurs RX 9060 XT, seule la variante au score le plus haut
    est conservée.
    **Complexité :** O(n), n = nombre de candidats classés.
    """
    resultat_final = []
    cles_vues = set()

    for resultat in resultats:
        caracteristiques = resultat.get("caracteristiques", {})
        valeur_diversite = caracteristiques.get("chipset") or caracteristiques.get(
            "famille"
        )

        if isinstance(valeur_diversite, str) and valeur_diversite.strip():
            cle = (
                caracteristiques.get("type"),
                valeur_diversite.strip().casefold(),
            )
            if cle in cles_vues:
                continue
            cles_vues.add(cle)

        resultat_final.append(resultat)
        if len(resultat_final) == top:
            break

    return resultat_final


def classer(candidats, entree, top=10):
    """Classe les candidats selon les règles et les poids liés à l'usage.

    **Reçoit :** `candidats`, les composants compatibles ; `entree`, les préférences
    de l'utilisateur, dont `usage` ; `top`, le nombre maximum de résultats.
    Exemple : une liste de cartes graphiques compatibles contenant la MSI GeForce RTX
    4070 Ventus, et `{"usage": "jeu"}`.

    **Renvoie :** au plus `top` dictionnaires triés par score décroissant, avec le
    score total, le détail des règles et les caractéristiques connues de la pièce.
    Une RTX 4070 peut ainsi apparaître avec son prix, son score, son score
    `perf_prix` et ses caractéristiques comme son chipset.

    **Complexité :** O(n × c + n log n + n × f), n = candidats, c = composants
    sélectionnés et f = nombre de caractéristiques de chaque pièce, avec une requête
    SQL par identifiant sélectionné.
    """
    poids = POIDS.get(entree["usage"], POIDS["jeu"])
    resultats = []
    entree_avec_fiches = entree.copy()
    entree_avec_fiches["composants"] = composants_selectionnes(entree)
    scores_perf_prix = normaliser_perf_prix(candidats)
    for index, piece in enumerate(candidats):
        detail = {
            "perf_prix": scores_perf_prix[index],
            "equilibre": regle_equilibre(piece, entree_avec_fiches),
            "alim": regle_alim(piece, entree_avec_fiches),
            "budget": regle_budget(piece, entree_avec_fiches),
        }
        score = sum(poids[k] * v for k, v in detail.items())
        # Choix : renvoyer les caractéristiques non vides dans un champ dédié permet
        # à l'interface de les afficher sans changer les champs déjà utilisés par elle.
        caracteristiques = {}
        for nom_champ, valeur in piece.items():
            if nom_champ not in ("id", "nom", "prix") and valeur is not None:
                caracteristiques[nom_champ] = valeur

        resultats.append({
            "id": piece["id"], "nom": piece["nom"], "prix": piece.get("prix"),
            "score": round(score, 3), "detail": detail,
            "caracteristiques": caracteristiques,
        })
    resultats.sort(key=obtenir_score, reverse=True)
    # Choix : garder le meilleur résultat par chipset/famille évite qu'une seule
    # génération remplisse le top 10 avec ses variantes de fabricants.
    return diversifier_resultats(resultats, top)
