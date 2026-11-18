"""Importe les fiches du catalogue PC dans PostgreSQL.

Responsable : A1 · Tâches 1, 2 et 7

Placer les six fichiers du catalogue dans `data/` ou `data/json/`, ainsi que
`data/all-gpus.json`, puis lancer :
`python -m scripts.import_catalogue`.
L'import est à lancer une seule fois pour éviter les doublons dans la base.
"""
from pathlib import Path

import pandas as pd

from models.db import get_connection
# Choix : réutiliser la même normalisation que l'enrichissement A2 évite que les deux
# jointures donnent des correspondances différentes pour un même chipset.
from scripts.enrichissement import norm

DOSSIER_DONNEES = Path("data")

# Choix : accepter `data/` et `data/json/` plutôt qu'un seul emplacement, car le guide
# indique `data/json/` tandis que le squelette initial attendait directement `data/`.
FICHIERS = {
    "cpu": "cpu.json",
    "carte_mere": "motherboard.json",
    "ram": "memory.json",
    "gpu": "video-card.json",
    "alim": "power-supply.json",
    "boitier": "case.json",
}

# Choix : filtrer à l'import plutôt que modifier les JSON sources, pour conserver les
# fichiers du catalogue intacts et pouvoir refaire l'import avec les critères du projet.
MICROARCHITECTURES_RECENTES = (
    "Zen 3",
    "Zen 4",
    "Zen 5",
    "Alder Lake",
    "Raptor Lake",
    "Raptor Lake Refresh",
    "Arrow Lake",
)
SOCKETS_RECENTS = ("AM4", "AM5", "LGA1700", "LGA1851")
# Choix : reconnaître les séries GeForce et les variantes RTX Ada récentes explicitement;
# un motif large « RTX 40/50 » inclurait aussi les anciens noms Quadro RTX 4000/5000.
MOTIF_GPU_RECENTES = (
    r"\bGeForce\s+RTX\s*(?:30|40|50)\d{2}\b"
    r"|\bRTX\s+(?:4000|5000)(?:\s+SFF)?\s+Ada\b"
    r"|\bRX\s*(?:6|7|9)\d{3}\b"
    r"|\bArc\b"
)

COLONNES_BDD = (
    "type",
    "nom",
    "prix",
    "microarchitecture",
    "nb_coeurs",
    "frequence_boost",
    "socket",
    "type_ram",
    "format",
    "chipset",
    "conso_w",
    "puissance_w",
    "tflops",
    "perf",
    "source",
)

REQUETE_INSERTION = """
    INSERT INTO composant (
        type, nom, prix, microarchitecture, nb_coeurs, frequence_boost,
        socket, type_ram, format, chipset, conso_w, puissance_w,
        tflops, perf, source
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def _chemin_fichier(nom_fichier):
    """Trouve le fichier JSON d'un type de pièce.

    **Reçoit :** `nom_fichier`, par exemple `"cpu.json"`.

    **Renvoie :** le chemin existant sous `data/` ou `data/json/`.

    **Exemple :** si `data/cpu.json` existe, `_chemin_fichier("cpu.json")`
    renvoie `Path("data/cpu.json")`.
    """
    chemins_possibles = (
        DOSSIER_DONNEES / nom_fichier,
        DOSSIER_DONNEES / "json" / nom_fichier,
    )
    for chemin in chemins_possibles:
        if chemin.is_file():
            return chemin

    chemins_attendus = " ou ".join(str(chemin) for chemin in chemins_possibles)
    raise FileNotFoundError(f"Fichier introuvable : {chemins_attendus}")


def _valeur(fiche, nom_champ):
    """Renvoie une valeur de fiche en remplaçant les valeurs manquantes par `None`.

    **Reçoit :** un dictionnaire de fiche et le nom d'un champ, par exemple
    `{"name": "AMD Ryzen 5 7600"}` et `"name"`.

    **Renvoie :** la valeur du champ, ou `None` si elle manque.

    **Exemple :** `_valeur({"name": "AMD Ryzen 5 7600"}, "name")` renvoie
    `"AMD Ryzen 5 7600"`.
    """
    valeur = fiche.get(nom_champ)
    if valeur is None:
        return None
    if isinstance(valeur, (list, tuple, dict)):
        return valeur
    if pd.isna(valeur):
        return None
    return valeur


def _type_ram(fiche):
    """Convertit la génération de mémoire du catalogue en `DDR4` ou `DDR5`.

    **Reçoit :** une fiche mémoire contenant éventuellement `speed`, par exemple
    `{"name": "Corsair Vengeance RGB 32 GB", "speed": [5, 6000]}`.

    **Renvoie :** `"DDR4"`, `"DDR5"` ou `None` si la génération ne correspond pas
    aux types acceptés par le schéma.

    **Exemple :** `_type_ram({"name": "Corsair Vengeance RGB 32 GB", "speed": [5, 6000]})`
    renvoie `"DDR5"`.

    **Complexité :** O(1), la fiche contient un nombre fixe de champs consultés.
    """
    vitesse = _valeur(fiche, "speed")
    if not isinstance(vitesse, (list, tuple)) or not vitesse:
        return None

    try:
        generation = int(vitesse[0])
    except (TypeError, ValueError):
        return None

    if generation in (4, 5):
        return f"DDR{generation}"
    return None


def _charger_tflops():
    """Charge les indices FP32 GPU depuis le fichier de la tâche 6.

    **Reçoit :** aucun argument ; lit `data/all-gpus.json`.

    **Renvoie :** un dictionnaire associant un nom de chipset normalisé à ses TFLOPS.

    **Exemple :** la fiche `GeForce RTX 4070` associe le chipset normalisé à `29.15` TFLOPS.

    **Complexité :** O(g), g = nombre de fiches dans `all-gpus.json`.
    """
    chemin = DOSSIER_DONNEES / "all-gpus.json"
    donnees = pd.read_json(chemin)
    tflops_par_chipset = {}

    for fiche in donnees.to_dict(orient="records"):
        nom = _valeur(fiche, "name")
        tflops = _valeur(fiche, "fp32")
        if isinstance(nom, str) and nom and tflops is not None:
            tflops_par_chipset[norm(nom)] = tflops

    return tflops_par_chipset


def _ajouter_performances(type_piece, donnees, tflops_par_chipset):
    """Calcule et normalise l'indice de performance d'un type de pièce.

    **Reçoit :** le type interne, un `DataFrame` filtré et le dictionnaire des TFLOPS.

    **Renvoie :** une copie du tableau avec `tflops` et `perf`. Le CPU utilise
    cœurs × fréquence boost, avec la fréquence de base en secours ; le GPU utilise
    les TFLOPS FP32. Chaque valeur est divisée par le maximum de son type puis
    multipliée par 100.

    **Exemple :** le Ryzen 5 7600 produit une valeur brute de 30.6 (6 × 5.1) ;
    une RTX 4070 utilise 29.15 TFLOPS avant normalisation dans son type.

    **Complexité :** O(n), n = nombre de pièces du type traité.
    """
    resultat = donnees.copy()
    resultat["tflops"] = None
    resultat["perf"] = None

    if type_piece == "cpu":
        coeurs = pd.to_numeric(resultat["core_count"], errors="coerce")
        frequence_boost = pd.to_numeric(resultat["boost_clock"], errors="coerce")
        if "core_clock" in resultat.columns:
            frequence_base = pd.to_numeric(resultat["core_clock"], errors="coerce")
        else:
            frequence_base = pd.Series(float("nan"), index=resultat.index)

        # Choix : la fréquence boost reste la référence. Quand le catalogue ne la
        # fournit pas, la fréquence de base donne un indice approximatif plutôt qu'un
        # perf nul qui rendrait le processeur inutilisable dans la règle d'équilibre.
        frequence = frequence_boost.fillna(frequence_base)
        performances_brutes = coeurs * frequence
    elif type_piece == "gpu":
        valeurs_tflops = []
        for chipset in resultat["chipset"]:
            if isinstance(chipset, str):
                valeur = tflops_par_chipset.get(norm(chipset))
            else:
                valeur = None
            valeurs_tflops.append(valeur)

        resultat["tflops"] = valeurs_tflops
        performances_brutes = pd.to_numeric(resultat["tflops"], errors="coerce")
    else:
        return resultat

    meilleure_performance = performances_brutes.max()
    if pd.isna(meilleure_performance) or meilleure_performance <= 0:
        return resultat

    resultat["perf"] = performances_brutes / meilleure_performance * 100
    return resultat


def _creer_ligne(type_piece, fiche):
    """Adapte les champs utiles du JSON aux colonnes de `composant`.

    **Reçoit :** le type interne de la pièce et sa fiche source. Exemple :
    `"gpu"` et une fiche de RTX 3060 avec `name`, `price` et `chipset`.

    **Renvoie :** un dictionnaire contenant les 15 colonnes à insérer, avec `None`
    pour les caractéristiques qui ne concernent pas ce type.

    **Exemple :** une fiche `MSI GeForce RTX 3060 Ventus 2X 12G`, à `299.97`,
    avec le chipset `GeForce RTX 3060 12GB` fournit le nom, le prix, le chipset,
    les TFLOPS associés et l'indice normalisé calculé en amont. Un CPU sans fréquence
    boost utilise la fréquence de base et l'indique dans `source`.
    """
    ligne = {colonne: None for colonne in COLONNES_BDD}
    ligne["type"] = type_piece
    ligne["nom"] = _valeur(fiche, "name")
    ligne["prix"] = _valeur(fiche, "price")
    ligne["tflops"] = _valeur(fiche, "tflops")
    ligne["perf"] = _valeur(fiche, "perf")

    if type_piece == "cpu":
        ligne["microarchitecture"] = _valeur(fiche, "microarchitecture")
        ligne["nb_coeurs"] = _valeur(fiche, "core_count")
        ligne["frequence_boost"] = _valeur(fiche, "boost_clock")
        ligne["conso_w"] = _valeur(fiche, "tdp")
        if ligne["perf"] is not None:
            if ligne["frequence_boost"] is None:
                ligne["source"] = (
                    "perf estimée : cœurs × fréquence de base, boost absent "
                    "(docyx/pc-part-dataset)"
                )
            else:
                ligne["source"] = (
                    "perf : cœurs × fréquence boost (docyx/pc-part-dataset)"
                )
    elif type_piece == "carte_mere":
        ligne["socket"] = _valeur(fiche, "socket")
        ligne["format"] = _valeur(fiche, "form_factor")
    elif type_piece == "ram":
        ligne["type_ram"] = _type_ram(fiche)
        if ligne["type_ram"] is not None:
            ligne["source"] = "type_ram : speed[0] (docyx/pc-part-dataset)"
    elif type_piece == "gpu":
        ligne["chipset"] = _valeur(fiche, "chipset")
        if ligne["tflops"] is not None and ligne["perf"] is not None:
            ligne["source"] = (
                "tflops : rightnow-ai/rightnow-gpu-database (fp32) ; "
                "perf : indice FP32 normalisé sur 100"
            )
    elif type_piece == "alim":
        ligne["puissance_w"] = _valeur(fiche, "wattage")
    elif type_piece == "boitier":
        ligne["format"] = _valeur(fiche, "type")

    return ligne


def _preparer_lignes(type_piece, donnees):
    """Transforme un tableau pandas en paramètres prêts pour l'insertion SQL.

    **Reçoit :** le type interne, puis les lignes du fichier sous forme de
    `DataFrame`. Exemple : `"gpu"` et les fiches du fichier `video-card.json`.

    **Renvoie :** une liste de tuples dans l'ordre de `COLONNES_BDD`.

    **Exemple :** une fiche RTX 3060 du fichier `video-card.json` devient un tuple
    commençant par `("gpu", "MSI GeForce RTX 3060 Ventus 2X 12G", 299.97, ...)`.

    **Complexité :** O(n × c), n = nombre de fiches et c = 15 colonnes insérées.
    """
    lignes = []
    for fiche in donnees.to_dict(orient="records"):
        ligne = _creer_ligne(type_piece, fiche)
        valeurs = tuple(ligne[colonne] for colonne in COLONNES_BDD)
        lignes.append(valeurs)
    return lignes


def _filtrer_generations(type_piece, donnees):
    """Garde les générations récentes définies dans le guide du chantier.

    **Reçoit :** le type interne de pièce et ses fiches dans un `DataFrame`.

    **Renvoie :** les lignes conservées : CPU Zen 3 à Zen 5 ou Intel récent,
    cartes mères AM4/AM5/LGA1700/LGA1851, RAM DDR4/DDR5 et GPU GeForce RTX 30/40/50,
    RX 6000/7000/9000 ou Arc. Les alimentations et boîtiers restent inchangés.

    **Exemple :** une fiche `AMD Ryzen 7 9800X3D` en microarchitecture `Zen 5`
    est conservée, tandis qu'une fiche `Zen 2` est écartée.

    **Complexité :** O(n), n = nombre de fiches dans le fichier.
    """
    if type_piece == "cpu":
        return donnees[
            donnees["microarchitecture"].isin(MICROARCHITECTURES_RECENTES)
        ]

    if type_piece == "carte_mere":
        return donnees[donnees["socket"].isin(SOCKETS_RECENTS)]

    if type_piece == "ram":
        lignes_recentes = []
        for fiche in donnees.to_dict(orient="records"):
            lignes_recentes.append(_type_ram(fiche) is not None)
        return donnees[lignes_recentes]

    if type_piece == "gpu":
        chipsets = donnees["chipset"].fillna("")
        masque = chipsets.str.contains(
            MOTIF_GPU_RECENTES, case=False, regex=True, na=False
        )
        return donnees[masque]

    return donnees


def main():
    """Importe le catalogue et les indices de performance dans `composant`.

    **Reçoit :** aucun argument.

    **Renvoie :** rien ; affiche le nombre de lignes importées pour chaque type.

    **Exemple :** `python -m scripts.import_catalogue` lit `video-card.json` et
    utilise `all-gpus.json` pour associer 29.15 TFLOPS à la GeForce RTX 4070.

    **Complexité :** O(n + g), n = fiches du catalogue et g = fiches GPU de référence.
    """
    tflops_par_chipset = _charger_tflops()
    nombres_importes = {}
    with get_connection() as connexion:
        with connexion.cursor() as curseur:
            for type_piece, nom_fichier in FICHIERS.items():
                chemin = _chemin_fichier(nom_fichier)
                donnees = pd.read_json(chemin)
                donnees = _filtrer_generations(type_piece, donnees)
                donnees = _ajouter_performances(
                    type_piece, donnees, tflops_par_chipset
                )
                lignes = _preparer_lignes(type_piece, donnees)
                curseur.executemany(REQUETE_INSERTION, lignes)
                nombres_importes[type_piece] = len(lignes)

    for type_piece, nombre in nombres_importes.items():
        print(f"{type_piece}: {nombre} lignes importées")


if __name__ == "__main__":
    main()
