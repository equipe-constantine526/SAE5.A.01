"""Enrichissement des données. Responsable : A2 (tâches 4, 5, 6).

- socket des CPU depuis data/microarch_socket.csv
- type de RAM des cartes mères (socket + "DDR4"/"D4" dans le nom)
- conso et alim conseillée des GPU depuis data/all-gpus.json (rightnow-gpu-database)
"""
import re


def norm(s):
    """Normalise un nom de chipset pour la jointure GPU. "RTX 3060 12GB LHR" -> "rtx 3060"."""
    s = s.lower().replace(" lhr", "")
    s = re.sub(r"\s*\d+\s*gb\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    # TODO A2
    pass


if __name__ == "__main__":
    main()
