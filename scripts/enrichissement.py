"""Enrichissement des données. Responsable : A2 (tâches 4, 5, 6).

- socket des CPU depuis data/microarch_socket.csv
- type de RAM des cartes mères (socket + "DDR4"/"D4" dans le nom)
- conso et alim conseillée des GPU depuis data/all-gpus.json (rightnow-gpu-database)
"""

from pathlib import Path
import re
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CHEMIN_MICROARCH = BASE_DIR / "data" / "microarch_socket.csv"


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


def main():
    cpus = pd.DataFrame([
        {"id": 101, "nom": "AMD Ryzen 5 7600"},
        {"id": 102, "nom": "AMD Ryzen 7 7800X3D"},
        {"id": 103, "nom": "Intel Core i5-13400F"},
        {"id": 104, "nom": "Intel Core i9-14900K"},
    ])

    resultat = enrichir_socket_cpu(cpus)
    print(resultat[["nom", "microarchitecture", "socket", "source"]].to_string(index=False))


if __name__ == "__main__":
    main()