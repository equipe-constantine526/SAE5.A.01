"""Import des configs relevées à la main. Responsables : C1 + C2 (tâche 25).

Lit data/configs.csv (export du Google Sheets), retrouve chaque pièce dans le catalogue
avec difflib, insère les configs (origine='corpus', validee=TRUE) et construit le graphe.
Les noms non trouvés sont écrits dans data/a_corriger.csv pour correction à la main.
"""
import difflib  # noqa: F401  (difflib.get_close_matches)


def main():
    # TODO C1
    pass


if __name__ == "__main__":
    main()
