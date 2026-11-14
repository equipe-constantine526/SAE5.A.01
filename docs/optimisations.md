# Journal des optimisations

Chaque optimisation est notée ici, dans la même pull request que le code, avec une mesure avant et après.
Point de départ : la version v0.1.0 (non optimisée, tag Git `v0.1.0`).

Modèle d'une entrée :

```markdown
## O-XX · Titre court (tâche N)

- **Problème :** ce qui était lent ou coûteux, et comment on l'a vu.
- **Version naïve :** ce que faisait le code. Complexité O(...), en précisant ce que représente chaque lettre.
- **Version optimisée :** ce qu'on a changé. Complexité O(...).
- **Mesure :** script utilisé, nombre d'exécutions, même machine.
  | | moyenne | min | max |
  |---|---|---|---|
  | avant | | | |
  | après | | | |
- **Contrepartie :** ce qu'on perd (mémoire, simplicité, cas non gérés).
- **Commit :** hash
```

---

<!-- Les entrées commencent ici, de la plus ancienne à la plus récente. -->
