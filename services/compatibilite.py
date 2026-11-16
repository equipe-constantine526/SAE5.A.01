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

def compatibles(config, type_cherche):
  """Renvoie les composants compatibles avec la configuration possédée.

  **Reçoit :** `config` (liste d'ids, ex. `[412]`), `type_cherche` (ex.
  `"carte_mere"`).
  **Renvoie :** liste de dicts des composants compatibles.
  **Exemple :** `compatibles([412], "carte_mere")` renvoie les cartes mères
  AM5.
  ******Complexité :** $O(p + n)$, $p =$ pièces possédées ($\\le 6$), $n =$.
  """
  if type_cherche not in {"cpu", "carte_mere", "ram", "gpu", "alim", "boitier"}:
    raise ValueError(f"Type de composant inconnu : {type_cherche}")

  possedes = (
      query("SELECT * FROM composant WHERE id = ANY(%s)", (config,))
      if config
      else []
  )
  conditions, params = [], [type_cherche]
  tdp_total = sum(p.get("tdp_w") or 0 for p in possedes)

  for p in possedes:
    paire = {type_cherche, p["type"]}
    if paire == {"cpu", "carte_mere"} and p.get("socket"):
      conditions.append("socket = %s")
      params.append(p["socket"])
    elif paire == {"ram", "carte_mere"} and p.get("type_ram"):
      conditions.append("type_ram = %s")
      params.append(p["type_ram"])
    elif (
        type_cherche == "alim"
        and p["type"] == "gpu"
        and p.get("alim_conseillee_w") is not None
    ):
      conditions.append("puissance_w >= %s")
      params.append(max(p["alim_conseillee_w"], tdp_total))
    elif (
        type_cherche == "gpu"
        and p["type"] == "alim"
        and p.get("puissance_w") is not None
    ):
      conditions.append(
          "(alim_conseillee_w IS NULL OR alim_conseillee_w <= %s)"
      )
      params.append(p["puissance_w"])

  sql = "SELECT * FROM composant WHERE type = %s" + (
      " AND " + " AND ".join(conditions) if conditions else ""
  )
  candidats = query(sql, tuple(params))

  # OPTI (P-01) : filtrage des formats boîtier / carte mère en Python
  # Maintenant : on filtre les formats en Python après la requête SQL (O(n)).
  # Pourquoi c'est améliorable : transfert SQL de lignes rejetées ensuite.
  # Piste : normaliser format à l'import et filtrer en SQL (WHERE format = ANY(%s)).
  # Gain attendu : à mesurer.
  for p in possedes:
    if type_cherche == "carte_mere" and p["type"] == "boitier":
      candidats = [c for c in candidats if format_compatible(c, p)]
    elif type_cherche == "boitier" and p["type"] == "carte_mere":
      candidats = [c for c in candidats if format_compatible(p, c)]

  return candidats

def config_valide(config):
  """Vérifie si une configuration complète est compatible.

  **Reçoit :** `config` (liste d'ids, ex. `[101, 201]`).
  **Renvoie :** `(True, None)` ou `(False, "raison")`.
  **Exemple :** `config_valide([101, 202])` -> `(False, "Socket
  incompatible...")`.
  ****Complexité :** $O(p)$, $p =$ nombre de pièces ($\\le 6$).
  """
  if not config:
    return True, None
  pieces = query("SELECT * FROM composant WHERE id = ANY(%s)", (config,))
  par_type = {p["type"]: p for p in pieces}
  cpu, cm, ram, gpu, alim, boitier = (
      par_type.get(t)
      for t in ("cpu", "carte_mere", "ram", "gpu", "alim", "boitier")
  )

  if (
      cpu
      and cm
      and cpu.get("socket")
      and cm.get("socket")
      and cpu["socket"] != cm["socket"]
  ):
    return False, "Socket incompatible entre le CPU et la carte mère."
  if (
      ram
      and cm
      and ram.get("type_ram")
      and cm.get("type_ram")
      and ram["type_ram"] != cm["type_ram"]
  ):
    return False, "Type de RAM incompatible avec la carte mère."
  if cm and boitier and not format_compatible(cm, boitier):
    return False, "Format de carte mère incompatible avec le boîtier."
  if alim and alim.get("puissance_w") is not None:
    tdp_total = sum(p.get("tdp_w") or 0 for p in pieces)
    seuil = max(
        (gpu.get("alim_conseillee_w") or 0) if gpu else 0, tdp_total
    )
    if alim["puissance_w"] < seuil:
      return False, "Puissance de l'alimentation insuffisante."
  return True, None

def rechercher(type_, texte):
  """Recherche des composants par nom pour l'autocomplétion (20 max).

  **Reçoit :** `type_` (`"gpu"`), `texte` (`"4070"`).
  **Renvoie :** liste de dicts `[{"id", "nom", "prix"}]`.
  **Exemple :** `rechercher("gpu", "4070")` -> `[{"id": 5521, "nom": "MSI RTX
  4070", "prix": 549}]`.
  """
  return query(
      "SELECT id, nom, prix FROM composant WHERE type = %s AND nom ILIKE %s"
      " ORDER BY nom LIMIT 20",
      (type_, f"%{texte}%"),
  )