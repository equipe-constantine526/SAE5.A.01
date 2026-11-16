"""Filtre de compatibilité, partagé par les deux méthodes. Responsable : A2 (tâche 8).

Règles à coder :
  - socket du processeur == socket de la carte mère
  - type de RAM == type accepté par la carte mère
  - puissance de l'alim >= alim conseillée de la carte graphique
  - format de la carte mère accepté par le boîtier
"""
"""Filtre de compatibilité, partagé par les deux méthodes. Responsable : A2 (tâche 8)."""

from models.db import query

FORMATS_ACCEPTES = {
    "E-ATX": {"E-ATX", "ATX", "Micro ATX", "Mini ITX"},
    "ATX": {"ATX", "Micro ATX", "Mini ITX"},
    "Micro ATX": {"Micro ATX", "Mini ITX"},
    "Mini ITX": {"Mini ITX"},
}


def normaliser_format(format_):
  """Uniformise un format de carte mère ou boîtier.

  **Reçoit :** `format_` (ex. `"Micro-ATX"`).
  **Renvoie :** `"E-ATX"`, `"ATX"`, `"Micro ATX"`, `"Mini ITX"` ou `None`.
  **Exemple :** `normaliser_format("mATX")` renvoie `"Micro ATX"`.
  """
  if not format_:
    return None
  f = format_.upper().replace(" ", "").replace("-", "").replace("_", "")
  if "EATX" in f:
    return "E-ATX"
  if "MICROATX" in f or "MATX" in f:
    return "Micro ATX"
  if "MINIITX" in f or f == "ITX":
    return "Mini ITX"
  return "ATX" if "ATX" in f else None


def format_compatible(carte_mere, boitier):
  """Vérifie si le boîtier accepte le format de la carte mère.

  **Reçoit :** `carte_mere` (dict) et `boitier` (dict).
  **Renvoie :** `True` si compatible ou format inconnu, `False` sinon.
  **Exemple :** `format_compatible({"format": "Micro ATX"}, {"format":
  "ATX"})` renvoie `True`.
  """
  f_cm = normaliser_format(carte_mere.get("format"))
  f_boitier = normaliser_format(boitier.get("format"))
  if f_cm is None or f_boitier is None:
    return True
  return f_cm in FORMATS_ACCEPTES.get(f_boitier, set())
