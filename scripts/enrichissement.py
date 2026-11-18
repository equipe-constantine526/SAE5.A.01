"""Complète les caractéristiques du catalogue en base PostgreSQL.

Responsable : A2 · Tâches 4, 5 et 6

- socket des CPU depuis data/microarch_socket.csv
- type de RAM des cartes mères (socket + "DDR4"/"D4" dans le nom)
- conso et alim conseillée des GPU depuis data/all-gpus.json (rightnow-gpu-database)
"""

from pathlib import Path
import re
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CHEMIN_MICROARCH = BASE_DIR / "data" / "microarch_socket.csv"
CHEMIN_GPU = BASE_DIR / "data" / "all-gpus.json"
CHEMIN_VIDEO_CARD = BASE_DIR / "data" / "video-card.json"

def norm(s):
    """Normalise un nom pour faciliter les jointures GPU."""
    if not isinstance(s, str):
        return ""
    s = s.lower().replace(" lhr", "")
    s = re.sub(r"\s*\d+\s*gb\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def trouver_microarchitecture(nom):
    """Déduit la microarchitecture à partir du nom d'un CPU."""
    if not isinstance(nom, str):
        return None

    nom = nom.lower()

    # AMD Ryzen
    if "ryzen" in nom:
        match = re.search(r"\b[3579]\s*(\d{4})", nom)
        if match:
            serie = int(match.group(1)[0])
            architectures = {
                1: "Zen",
                2: "Zen+",
                3: "Zen 2",
                5: "Zen 3",
                7: "Zen 4",
                8: "Zen 4",
                9: "Zen 5",
            }
            return architectures.get(serie)

    # Intel Core
    match = re.search(r"\bi[3579]\s*[- ]?(\d{4,5})", nom)
    if match:
        generation = match.group(1)[:2]
        architectures = {
            "10": "Comet Lake",
            "11": "Rocket Lake",
            "12": "Alder Lake",
            "13": "Raptor Lake",
            "14": "Raptor Lake Refresh",
        }
        return architectures.get(generation)

    # Intel Core Ultra 200
    if re.search(r"\bcore\s+ultra\s+[579]\s+2\d{2}\b", nom):
        return "Arrow Lake"

    return None


def enrichir_socket_cpu(df_cpu):
    """Ajoute la microarchitecture et le socket à chaque CPU."""
    correspondances = pd.read_csv(CHEMIN_MICROARCH, dtype=str)
    for col in correspondances.columns:
        correspondances[col] = correspondances[col].str.strip()

    df_cpu = df_cpu.copy()

    if "microarchitecture" not in df_cpu.columns:
        df_cpu["microarchitecture"] = pd.NA

    df_cpu["microarchitecture"] = (
        df_cpu["microarchitecture"]
        .replace(r"^\s*$", pd.NA, regex=True)
        .fillna(df_cpu["nom"].apply(trouver_microarchitecture))
    )

    df_cpu = df_cpu.drop(columns=["socket", "source"], errors="ignore")

    return df_cpu.merge(
        correspondances[["microarchitecture", "socket", "source"]],
        on="microarchitecture",
        how="left"
    )


def enrichir_type_ram_cm(df_cm):
    """Déduit le type de RAM accepté par chaque carte mère."""
    df_cm = df_cm.copy()

    def determiner_ram(ligne):
        socket = str(ligne.get("socket") or "").strip().upper()
        nom = ligne.get("nom")

        if socket == "AM4":
            return "DDR4", True

        if socket in ["AM5", "LGA1851"]:
            return "DDR5", True

        if socket == "LGA1700":
            if isinstance(nom, str) and re.search(
                r"\b(?:DDR4|D4)\b", nom, re.IGNORECASE
            ):
                return "DDR4", True

            return "DDR5", False

        return pd.NA, False

    resultat = df_cm.apply(determiner_ram, axis=1)

    df_cm["type_ram"] = resultat.apply(lambda x: x[0])
    df_cm["verifie"] = resultat.apply(lambda x: x[1])

    return df_cm
def enrichir_infos_gpu():
    """Enrichit les GPU docyx avec les informations RightNow."""

    df_gpu = pd.read_json(CHEMIN_VIDEO_CARD)
    base_gpu = pd.read_json(CHEMIN_GPU)

    colonnes = ["name", "tdp", "suggestedPSU"]

    for col in colonnes:
        if col not in base_gpu.columns:
            raise ValueError(f"Colonne {col} absente de all-gpus.json")

    df_gpu["nom_normalise"] = df_gpu["chipset"].apply(norm)
    base_gpu["nom_normalise"] = base_gpu["name"].apply(norm)

    base_gpu = base_gpu.drop_duplicates(
        subset=["nom_normalise"],
        keep="first"
    )

    resultat = df_gpu.merge(
        base_gpu[["nom_normalise", "tdp", "suggestedPSU"]],
        on="nom_normalise",
        how="left"
    )

    return resultat.drop(columns=["nom_normalise"])


def _valeur_sql(valeur):
    """Convertit une valeur pandas en valeur simple acceptée par PostgreSQL.

    **Reçoit :** une valeur scalaire, éventuellement `pd.NA` ou `NaN`.
    **Renvoie :** `None` pour une valeur manquante, sinon sa valeur Python.
    **Exemple :** `_valeur_sql(pd.NA)` renvoie `None`.
    **Complexité :** O(1).
    """
    if pd.isna(valeur):
        return None
    if hasattr(valeur, "item"):
        return valeur.item()
    return valeur


def _fusionner_source(source_existante, nouvelle_source):
    """Ajoute une origine sans écraser les autres ni la dupliquer.

    **Reçoit :** les sources actuelles et une nouvelle source, par exemple
    `"perf : cœurs × fréquence boost"` et `"socket : microarch_socket.csv"`.
    **Renvoie :** les sources séparées par `; `, chacune présente une seule fois.
    **Exemple :** deux appels successifs avec la source socket ne la répètent pas.
    **Complexité :** O(s), s = nombre de sources déjà enregistrées.
    """
    sources = [
        source.strip()
        for source in (source_existante or "").split(";")
        if source.strip()
    ]
    if nouvelle_source and nouvelle_source not in sources:
        sources.append(nouvelle_source)
    return "; ".join(sources) or None


def _en_entier(valeur):
    """Convertit un wattage en entier SQL ou renvoie `None` s'il est invalide.

    **Reçoit :** une valeur numérique ou manquante, par exemple `550.0`.
    **Renvoie :** un entier ou `None` si la valeur est absente ou invalide.
    **Exemple :** `_en_entier(550.0)` renvoie `550`.
    **Complexité :** O(1).
    """
    valeur = _valeur_sql(valeur)
    if valeur is None:
        return None
    try:
        return int(round(float(valeur)))
    except (TypeError, ValueError):
        return None


def main():
    """Enrichit en base les sockets, types de RAM et wattages manquants.

    **Reçoit :** aucun argument ; lit les fichiers `data/` et PostgreSQL.
    **Renvoie :** rien ; met à jour les lignes de `composant` et affiche les nombres
    de lignes traitées.
    **Exemple :** un CPU `AMD Ryzen 5 7600` reçoit son socket AM5, et un GPU reconnu
    reçoit sa consommation et son alimentation conseillée.
    **Complexité :** O(c + m + g), c = CPU, m = cartes mères, g = GPU importés.
    """
    from models.db import get_connection

    nombres = {"cpu": 0, "carte_mere": 0, "gpu": 0}
    source_ram = "type_ram : déduit du socket et du nom de la carte mère"
    source_ram_suppose = (
        "type_ram : hypothèse DDR5, faute de mention DDR4 sur une carte LGA1700"
    )
    source_gpu = (
        "conso_w et alim_conseillee_w : rightnow-ai/rightnow-gpu-database "
        "(jointure sur le chipset)"
    )

    # OPTI (P-16) : mise à jour SQL composant par composant lors de l'import.
    #   Maintenant : chaque ligne enrichie déclenche un UPDATE séparé.
    #   Pourquoi c'est améliorable : plusieurs milliers d'allers-retours peuvent
    #   ralentir ce script, même s'il ne tourne qu'après un import.
    #   Piste : préparer les lignes puis utiliser executemany par type de composant.
    #   Gain attendu : à mesurer (durée totale du script d'enrichissement).
    with get_connection() as connexion:
        with connexion.cursor() as curseur:
            curseur.execute(
                """SELECT id, nom, microarchitecture, source
                   FROM composant WHERE type = %s""",
                ("cpu",),
            )
            cpus = pd.DataFrame(curseur.fetchall())
            if not cpus.empty:
                sources_cpu = dict(zip(cpus["id"], cpus["source"]))
                cpus_enrichis = enrichir_socket_cpu(cpus)
                for ligne in cpus_enrichis.to_dict(orient="records"):
                    socket = _valeur_sql(ligne.get("socket"))
                    if socket is None:
                        continue
                    source = _fusionner_source(
                        sources_cpu.get(ligne["id"]),
                        _valeur_sql(ligne.get("source")),
                    )
                    curseur.execute(
                        """UPDATE composant
                           SET microarchitecture = %s, socket = %s, source = %s
                           WHERE id = %s""",
                        (
                            _valeur_sql(ligne.get("microarchitecture")),
                            socket,
                            source,
                            ligne["id"],
                        ),
                    )
                    nombres["cpu"] += 1

            curseur.execute(
                """SELECT id, nom, socket, source
                   FROM composant WHERE type = %s""",
                ("carte_mere",),
            )
            cartes_meres = pd.DataFrame(curseur.fetchall())
            if not cartes_meres.empty:
                cartes_meres_enrichies = enrichir_type_ram_cm(cartes_meres)
                for ligne in cartes_meres_enrichies.to_dict(orient="records"):
                    type_ram = _valeur_sql(ligne.get("type_ram"))
                    if type_ram is None:
                        continue
                    source_ram_ligne = source_ram
                    if not _valeur_sql(ligne.get("verifie")):
                        source_ram_ligne = source_ram_suppose
                    source = _fusionner_source(
                        ligne.get("source"), source_ram_ligne
                    )
                    curseur.execute(
                        """UPDATE composant
                           SET type_ram = %s, type_ram_verifie = %s, source = %s
                           WHERE id = %s""",
                        (
                            type_ram,
                            _valeur_sql(ligne.get("verifie")),
                            source,
                            ligne["id"],
                        ),
                    )
                    nombres["carte_mere"] += 1

            curseur.execute(
                """SELECT id, chipset, source
                   FROM composant WHERE type = %s""",
                ("gpu",),
            )
            gpu_catalogue = pd.DataFrame(curseur.fetchall())
            if not gpu_catalogue.empty:
                gpu_donnees = enrichir_infos_gpu()
                gpu_catalogue["chipset_normalise"] = gpu_catalogue["chipset"].apply(norm)
                gpu_donnees["chipset_normalise"] = gpu_donnees["chipset"].apply(norm)
                gpu_donnees = gpu_donnees[
                    gpu_donnees["chipset_normalise"] != ""
                ]
                gpu_donnees = gpu_donnees.drop_duplicates(
                    subset=["chipset_normalise"], keep="first"
                )
                gpu_enrichis = gpu_catalogue.merge(
                    gpu_donnees[["chipset_normalise", "tdp", "suggestedPSU"]],
                    on="chipset_normalise",
                    how="left",
                )
                for ligne in gpu_enrichis.to_dict(orient="records"):
                    consommation = _en_entier(ligne.get("tdp"))
                    alim_conseillee = _en_entier(ligne.get("suggestedPSU"))
                    if consommation is None and alim_conseillee is None:
                        continue
                    source = _fusionner_source(ligne.get("source"), source_gpu)
                    curseur.execute(
                        """UPDATE composant
                           SET conso_w = COALESCE(%s, conso_w),
                               alim_conseillee_w = COALESCE(%s, alim_conseillee_w),
                               source = %s
                           WHERE id = %s""",
                        (consommation, alim_conseillee, source, ligne["id"]),
                    )
                    nombres["gpu"] += 1

    for type_piece, nombre in nombres.items():
        print(f"{type_piece} : {nombre} composants enrichis")


if __name__ == "__main__":
    main()
