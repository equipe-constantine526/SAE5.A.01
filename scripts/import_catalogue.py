"""Import du catalogue docyx/pc-part-dataset. Responsable : A1 (tâches 1, 2, 7).

Lancer une seule fois : python -m scripts.import_catalogue
Mettre les JSON téléchargés dans data/ (dossier ignoré par Git).
"""
import pandas as pd

FICHIERS = {
    "cpu": "data/cpu.json",
    "carte_mere": "data/motherboard.json",
    "ram": "data/memory.json",
    "gpu": "data/video-card.json",
    "alim": "data/power-supply.json",
    "boitier": "data/case.json",
}


def main():
    for type_, chemin in FICHIERS.items():
        df = pd.read_json(chemin)
        # TODO A1 : filtre des générations récentes (tâche 2), puis INSERT dans composant
        print(f"{type_}: {len(df)} lignes lues")


if __name__ == "__main__":
    main()
