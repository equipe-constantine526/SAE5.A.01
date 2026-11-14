# RigMatch : contexte du projet pour Claude Code

Projet de SAÉ BUT3 Informatique (5.Real.01, IUT Sorbonne Paris Nord), équipe de 6 étudiants.
Application web qui recommande des composants PC compatibles et **compare deux méthodes de recommandation**.

## Règles de travail avec Claude (à respecter en priorité)

Le sujet est clair : à l'oral, chaque membre doit pouvoir expliquer **tout** ce qui est rendu, sinon la note chute. Le code est généré avec l'aide de l'IA, donc il doit être écrit pour être **compris et défendu par nous**. C'est la règle numéro un, avant la performance ou l'élégance.

### Interdit : aucune mention de Claude dans le dépôt

- **JAMAIS de co-authoring.** Aucune ligne `Co-Authored-By`, aucun « Generated with Claude Code », aucune signature ou mention de Claude ou d'une IA dans les messages de commit, les descriptions de pull request, le code, les commentaires ou la documentation.
- Les messages de commit sont écrits comme par un membre de l'équipe : courts, en français, au présent. Exemple : `Ajoute la règle d'équilibre CPU/GPU (tâche 16)`.

### Écrire du code compréhensible

- **Niveau BUT3 :** code simple et lisible plutôt que malin. Pas de design pattern, de librairie ou d'abstraction en plus si ce n'est pas nécessaire. Si une solution plus avancée existe, propose-la, ne l'impose pas.
- **Chaque fonction a une docstring** qui dit : à quoi elle sert, ce qu'elle reçoit, ce qu'elle renvoie, **avec un exemple concret** de nos données (un vrai nom de pièce, un vrai chiffre). Format imposé : voir la section « Documentation » (elle sert à générer la doc automatiquement).
- **Les commentaires expliquent le POURQUOI, pas le quoi.** Pas de `# boucle sur les pièces` au-dessus d'un `for`. Oui à `# On ramène le score entre 0 et 1, sinon une règle à grande échelle (le prix en €) écraserait les autres`.
- **Chaque choix discutable est justifié dans un commentaire `# Choix :`**, avec l'alternative écartée et la raison. Ce sont exactement les questions de l'oral. Exemple :
  ```python
  # Choix : on stocke les liens du graphe en base (table lien_graphe) plutôt que de
  # recalculer le graphe à chaque requête. Recalculer = parcourir les 300 configs à
  # chaque recommandation ; stocker = une seule lecture. En contrepartie, chaque ajout
  # de config doit mettre à jour les liens (voir ajouter_liens).
  ```
- **Les parties algorithmiques indiquent leur complexité** en commentaire, avec ce que représente chaque lettre. Exemple : `# Complexité : O(n × r), n = nombre de pièces candidates, r = nombre de règles (4)`.
- Pas de code « magique » : pas de compréhension de liste imbriquée sur trois niveaux, pas de lambda compliquée, pas de raccourci obscur. Si une ligne demande plus de 10 secondes pour être comprise, découpe-la.
- Noms de variables, fonctions et commentaires en **français**, comme dans le reste du code.

### Après chaque modification, dans la réponse (pas dans le code)

1. **Explique ce que fait le code** en quelques phrases simples, avec un exemple d'entrée et de sortie.
2. **Donne 2 ou 3 questions qu'un prof pourrait poser** sur ce code à l'oral, avec une réponse courte.
3. **Signale ce qui reste fragile ou approximatif** (cas non gérés, valeurs estimées).

### Périmètre

- **Ne modifie que les fichiers de la tâche en cours.** Chaque fichier a un responsable (voir plus bas). Si une modification est nécessaire ailleurs, signale-la au lieu de la faire.
- **Ne change jamais le contrat d'API** (routes et format des JSON) sans le dire explicitement : les autres binômes en dépendent.
- Pas de données factices présentées comme réelles. Les valeurs estimées sont signalées comme telles.

## Optimisation : chaque amélioration doit être prouvée par un exemple concret

À la présentation, nous devons pouvoir dire « voilà ce qui était lent, voilà ce qu'on a changé, voilà le gain mesuré ». Une optimisation sans mesure avant/après ne vaut rien pour la compétence Optimisation.

**Règles :**
- **Jusqu'au 18 novembre : on n'optimise rien, mais on repère.** On écrit la version naïve et lisible (c'est notre point de départ), et on marque chaque endroit améliorable avec un commentaire `# OPTI :` (voir ci-dessous).
- **On mesure avant de changer quoi que ce soit.** Pas d'optimisation « au cas où ».
- **On garde la version naïve** (dans l'historique Git avec un tag, ou dans une fonction `..._naif()` à côté) pour pouvoir refaire la comparaison devant le jury.
- **Chaque optimisation est notée dans `docs/optimisations.md`**, dans la même pull request que le code. Claude doit la rédiger à chaque fois qu'il optimise quelque chose.

### Commentaires `# OPTI :` aux endroits améliorables

Les pistes connues sont listées et numérotées (`P-XX`) dans **`docs/pistes_optimisation.md`**, avec les choix déjà faits (`C-XX`). Dès que Claude écrit du code qui pourrait être plus rapide ou moins gourmand, il ajoute **juste au-dessus** un commentaire `# OPTI (P-XX) :` qui reprend le numéro de la piste (si la piste n'existe pas encore, il l'ajoute au document dans la même modification). Le commentaire suit ce format : `# OPTI :` (ou `// OPTI :` en JavaScript et Vue) qui explique **comment ça marche maintenant**, **pourquoi c'est améliorable** et **comment on compte faire mieux**. Pour les points qui concernent la batterie ou l'énergie, on écrit `# OPTI (énergie) :`. Modèle :

```python
# OPTI : filtrage des cartes mères compatibles
#   Maintenant : on récupère toutes les cartes mères de la base, puis on garde en Python
#                celles qui ont le bon socket. Complexité O(n), n = nombre total de
#                cartes mères dans la base.
#   Pourquoi c'est améliorable : à chaque requête, toute la table est transférée de
#                PostgreSQL vers Python, alors qu'on n'en garde qu'une partie.
#   Piste : filtrer directement en SQL (WHERE socket = %s) et ajouter un index sur la
#           colonne socket : la base ne lit plus que les lignes utiles.
#   Gain attendu : à mesurer (temps de /api/recommend/content avant et après).
```

```js
// OPTI (énergie) : appels de l'autocomplétion
//   Maintenant : une requête à l'API à chaque lettre tapée (« 4070 » = 4 requêtes).
//   Pourquoi c'est améliorable : requêtes inutiles, réseau et batterie sollicités.
//   Piste : attendre 300 ms sans frappe avant d'appeler l'API (debounce).
//   Gain attendu : à mesurer (nombre de requêtes pour une même saisie).
```

Règles :
- **Jamais de chiffre inventé** dans « Gain attendu » : on écrit « à mesurer » et ce qu'on mesurera.
- **Une fois l'optimisation faite**, la piste passe au statut « fait (O-XX) » dans `docs/pistes_optimisation.md`, et le commentaire devient `# OPTIMISÉ (O-XX) :`, avec en une ou deux lignes l'avant, l'après et le renvoi vers l'entrée de `docs/optimisations.md`. On garde ainsi la trace de l'ancien fonctionnement à l'endroit même du code.
- **Lister tous les points à optimiser** (base directe du rapport du 2 décembre, section « identification des points à optimiser » et « points pour économiser la batterie ») :
  ```bash
  grep -rn "OPTI" --include=*.py --include=*.vue --include=*.js --include=*.sql . | grep -v node_modules
  ```

### Journal `docs/optimisations.md`

**Modèle d'une entrée dans `docs/optimisations.md`** (les chiffres ci-dessous sont **fictifs**, juste pour montrer le format ; ne jamais écrire de mesure qui n'a pas été faite) :

```markdown
## O-03 · Mise à jour incrémentale des liens du graphe (tâche 29)

- **Problème :** à chaque config ajoutée, on recalculait tous les liens à partir des 300 configs.
- **Version naïve :** parcours de toutes les configs, toutes les paires. Complexité O(c × k²), c = nombre de configs, k = pièces par config.
- **Version optimisée :** on n'ajoute que les paires de la nouvelle config. Complexité O(k²), soit 15 paires pour 6 pièces.
- **Mesure :** script `scripts/bench_graphe.py`, 50 exécutions, même machine.
  | | moyenne | min | max |
  |---|---|---|---|
  | avant | 412 ms | 398 ms | 455 ms |
  | après | 3 ms | 2 ms | 6 ms |
- **Contrepartie :** si une config est supprimée, il faut retirer ses paires à la main.
- **Commit :** `a1b2c3d`
```

**Pistes déjà identifiées pour après le 18** (à mesurer avant de les faire) : index SQL sur les colonnes filtrées (`type`, `socket`) ; filtrer les candidats en SQL plutôt qu'en Python ; mise à jour incrémentale des liens du graphe ; nombre d'itérations de la marche aléatoire (arrêter quand le classement ne bouge plus) ; matrice creuse pour le graphe ; cache des recommandations fréquentes. Pour la batterie et l'énergie : moins de requêtes du front (attendre 300 ms avant d'appeler l'autocomplétion), réponses JSON plus légères, pas de recalcul inutile.

## Documentation

La documentation du code est **générée automatiquement** à partir des docstrings avec **pdoc** (backend). Une docstring mal écrite = une doc illisible, donc le format ci-dessous est obligatoire.

### Format des docstrings (Python, en Markdown)

En haut de **chaque fichier**, une docstring de module : son rôle, le responsable, les tâches concernées.

```python
"""Filtre de compatibilité, partagé par les deux méthodes de recommandation.

Responsable : A2 · Tâches 8 et 10
"""
```

Pour **chaque fonction** :

```python
def compatibles(composants_ids, type_cherche):
    """Renvoie les pièces d'un type donné qui sont compatibles avec la config de l'utilisateur.

    **Reçoit :**
    - `composants_ids` : ids des pièces que l'utilisateur possède déjà, ex. `[412]` (un Ryzen 5 7600, socket AM5)
    - `type_cherche` : type de pièce voulu, ex. `"carte_mere"`

    **Renvoie :** une liste de dictionnaires, un par pièce compatible,
    ex. `[{"id": 2981, "nom": "MSI B650 Tomahawk", "socket": "AM5", ...}]`

    **Exemple :** `compatibles([412], "carte_mere")` renvoie toutes les cartes mères AM5.

    **Complexité :** O(n), n = nombre de pièces du type cherché.
    """
```

La ligne **Complexité** est obligatoire pour les fonctions algorithmiques (compatibilité, score, graphe), facultative ailleurs.

### Générer la doc

```bash
pdoc -d markdown ./app.py controllers services models scripts            # doc en direct sur http://localhost:8080
pdoc -d markdown ./app.py controllers services models scripts -o docs/code   # génère le site HTML dans docs/code/
```

On régénère `docs/code/` et on le committe **avant chaque rendu** (18 novembre, 15 janvier), pour que les enseignants puissent l'ouvrir sans rien installer.

### Frontend

Pas de générateur pour l'instant. Chaque composant Vue commence par un commentaire qui dit son rôle et son responsable, et chaque fonction a un commentaire JSDoc :

```js
/**
 * Cherche les composants dont le nom contient le texte tapé (autocomplétion).
 * @param {string} type  Type de pièce, ex. "gpu"
 * @param {string} texte Texte tapé par l'utilisateur, ex. "4070"
 * @returns {Promise<Array>} ex. [{ id: 5521, nom: "MSI GeForce RTX 4070 Ventus", prix: 549 }]
 */
```

### Les autres documents

- `README.md` : installation, lancement, contrat d'API. Mis à jour dès que l'un des trois change.
- `docs/pistes_optimisation.md` : choix déjà faits pour la performance (`C-XX`) et pistes connues à optimiser (`P-XX`).
- `docs/optimisations.md` : journal des optimisations réellement faites et mesurées (`O-XX`).
- `CHANGELOG.md` : ce que contient chaque version taggée.
- `docs/decisions.md` : journal des décisions (voir « Qualité et gestion de projet »).
- `docs/reunions/` : comptes-rendus de réunion.

## Ce que fait l'application

L'utilisateur donne son budget, son usage (jeu, montage, bureautique), les composants qu'il possède déjà et le type de pièce cherché. L'application propose des pièces compatibles avec deux méthodes, et un dashboard compare leurs résultats et leurs performances.

1. **Filtre de compatibilité** (commun, appliqué AVANT les deux méthodes) : socket CPU = socket carte mère, type de RAM = celui de la carte mère, alim ≥ alim conseillée du GPU, format carte mère accepté par le boîtier. Les deux méthodes classent donc les mêmes candidats.
2. **Méthode 1, basée sur le contenu** (`services/score_contenu.py`) : score = somme pondérée de règles sur les fiches techniques (perf/prix, équilibre CPU/GPU, marge d'alim, budget). Poids différents selon l'usage. Aucune donnée d'utilisateurs.
3. **Méthode 2, par graphe** (`services/graphe.py`) : nœuds = composants, lien entre deux composants s'ils apparaissent ensemble dans une configuration réelle, poids = nombre de configs. Recommandation par **Personalized PageRank** (marche aléatoire qui revient aux pièces de l'utilisateur avec une probabilité de 15 %). Les deux méthodes doivent rester vraiment différentes : la méthode 1 n'utilise pas la popularité, la méthode 2 n'utilise pas les fiches techniques.

Décisions déjà prises (ne pas revenir dessus sans en parler à l'équipe) :
- pas de comptes utilisateurs ni d'espace admin ; la saisie est gardée dans le **localStorage** du navigateur ;
- pas de notes d'utilisateurs (aucune donnée de notes n'existe) ;
- pas d'API extérieure : les données sont des fichiers téléchargés une fois et importés dans PostgreSQL ;
- la sécurité n'est pas évaluée : seulement les réflexes de base (ci-dessous).

## Stack et architecture

- **Backend :** Python, Flask, psycopg (PostgreSQL), pandas. `networkx` seulement pour le prototype de la méthode 2.
- **Frontend :** Vue.js (dans `frontend/`), Chart.js pour le dashboard. Ne parle au backend que par l'API.
- **Base :** PostgreSQL, schéma dans `models/schema.sql`.

```
app.py            point d'entrée, enregistre les routes (blueprints)
controllers/      routes : lisent la requête, appellent UN service, renvoient du JSON. AUCUN calcul ici.
services/         toute la logique (compatibilité, méthode 1, méthode 2, configs, mesures)
models/db.py      connexion et fonctions query() / execute()
models/schema.sql tables
scripts/          import et enrichissement des données, lancés une seule fois
tests/            pytest
frontend/         application Vue
data/             fichiers de données téléchargés (ignoré par Git)
```

## Contrat d'API

| Route | Entrée | Sortie |
|---|---|---|
| `GET /api/health` | | `{"status": "ok"}` |
| `GET /api/composants?type=gpu&q=4070` | | `[{"id", "nom", "prix"}]` (20 max) |
| `POST /api/recommend/content` | `{"composants": [ids], "budget", "usage", "type_cherche"}` | `{"resultats": [{"id", "nom", "prix", "score", "detail"?}], "temps_ms"}` |
| `POST /api/recommend/graph` | même entrée | même sortie |
| `POST /api/configs` | `{"composants": [ids]}` | 201 `{"id"}` ou 400 `{"erreur": "raison"}` |
| `GET /api/stats` | | `[{"methode", "min", "max", "moyenne", "nb"}]` |

Les deux routes de recommandation ont **exactement** le même format, sinon le dashboard ne peut pas comparer. Elles passent toutes les deux par `_recommander()` dans `controllers/recommandation.py` (compatibilité, puis classement, puis chronométrage).

## Règles de code obligatoires

- **Requêtes SQL toujours paramétrées :** `query("... WHERE id = %s", (id_saisi,))`. Jamais de f-string avec une valeur venant de l'utilisateur.
- **Le filtre de compatibilité tourne côté backend**, jamais seulement dans le front.
- Les types de composants s'écrivent : `cpu`, `carte_mere`, `ram`, `gpu`, `alim`, `boitier`.
- Dans `lien_graphe`, toujours `a < b` (une paire n'est stockée qu'une fois).
- Côté Vue, pas de `v-html`. Lectures et écritures du localStorage entourées d'un try/catch.

## Données

- **Catalogue :** `docyx/pc-part-dataset` (GitHub, licence MIT), fichiers JSON `cpu`, `motherboard`, `memory`, `video-card`, `power-supply`, `case`. Prix en dollars. On ne garde que les générations récentes : CPU Zen 3+ / Alder Lake+, sockets AM4, AM5, LGA1700, LGA1851, GPU RTX 30-50, RX 6000-9000, Arc.
- **Enrichissement :** socket des CPU déduit de la microarchitecture (petite table CSV) ; type de RAM des cartes mères déduit du socket (LGA1700 : « DDR4 » ou « D4 » dans le nom, sinon DDR5) ; conso et alim conseillée des GPU depuis `rightnow-ai/rightnow-gpu-database` (`all-gpus.json`, champs `tdp` et `suggestedPSU`), jointure sur le chipset normalisé avec `norm()` ; perf GPU = TFLOPS FP32, perf CPU = cœurs × fréquence boost, ramenées sur 100. Chaque valeur ajoutée garde sa source.
- **Configurations réelles :** environ 300, relevées à la main (PCPartPicker Completed Builds, archive Maximum PC) dans un CSV, importées par `scripts/import_corpus.py`. Les nœuds du graphe sont des **familles** de pièces (ex. « RTX 4070 »), pas des références exactes.

## Commandes

```bash
pip install -r requirements.txt
psql -d rigmatch -f models/schema.sql
python app.py                 # http://localhost:5000/api/health
pytest
pdoc -d markdown ./app.py controllers services models scripts   # doc du code sur http://localhost:8080
grep -rn "OPTI" --include=*.py --include=*.vue --include=*.js --include=*.sql . | grep -v node_modules   # points à optimiser
cd frontend && npm run dev    # http://localhost:5173
```

## Tâches et responsables

Les tâches sont numérotées comme dans le tableau GitHub Projects et le Guide des chantiers.

| Binôme | Fichiers |
|---|---|
| A1 (tâches 1-3, 7, 11, 13) | `scripts/import_catalogue.py`, `models/schema.sql`, `frontend/src/views/Saisie.vue` |
| A2 (tâches 4-6, 8-10, 12) | `scripts/enrichissement.py`, `services/compatibilite.py`, `controllers/composants.py`, `tests/test_compatibilite.py`, `frontend/src/components/RechercheComposant.vue` |
| B1 (tâches 15-18, 22) | `services/score_contenu.py`, `frontend/src/views/Resultats.vue` (création) |
| B2 (tâches 14, 19-21, 23) | `tests/donnees_factices.json`, `controllers/recommandation.py`, `services/enchainement.py`, `services/mesures.py`, `controllers/stats.py` |
| C1 (tâches 24-28) | `scripts/import_corpus.py`, `services/configs.py`, `controllers/configs.py`, `frontend/src/views/AjouterConfig.vue` |
| C2 (tâches 29-32) | `services/graphe.py`, bouton « méthode graphe » dans `Resultats.vue` |

## Le sujet (résumé, le PDF complet est dans `docs/sujet_SAE.pdf`)

Évaluation par 3 compétences de poids égal :
- **Développement** (G. Guibon) : concevoir, coder, tester et intégrer l'application.
- **Optimisation** (P. Siest) : l'algorithme de recommandation, sa complexité, son temps d'exécution, la consommation d'énergie.
- **Communication** (P. Hellégouarc'h) : l'interface, le branding, le rapport, le travail en équipe (Git, GitHub Projects).

Fonctionnalités obligatoires de la version finale : deux approches de recommandation, évaluation de leur complexité, temps de réponse min/max/moyen, interface justifiée (pourquoi cette recommandation, en quoi l'interface y répond), dashboard visuel de comparaison **à la fin de chaque recommandation**, licence open source justifiée. Ajouts possibles mais sans surcharger l'application.

**Sur l'IA :** à l'oral, l'équipe sera interrogée sur tout ce qui est rendu (code, rapports). Tout ce que Claude écrit doit pouvoir être expliqué par n'importe quel membre. D'où les règles en haut de ce fichier.

## Rendu du 18 novembre : version v0.1.0 (TÂCHE EN COURS)

Ce que le sujet demande pour cette date :
- interface **complète** mais pas forcément jolie ;
- backend en place avec **Controllers et Services** ;
- modèle (BDD) **pas obligatoirement finalisé** ;
- recommandation et application **pas encore optimisées** ;
- une **recommandation unique** suffit (la méthode 1).

### Dans la v0.1.0

- **Méthode 1 de bout en bout :** saisie → `/api/recommend/content` → liste classée avec score et détail du score.
- **Filtre de compatibilité réel** côté backend (au moins socket CPU/carte mère et type de RAM ; alim et boîtier si le temps le permet).
- **Toutes les pages existent et sont reliées à l'API :** Saisie (avec autocomplétion et localStorage), Résultats, Ajouter ma config. Mise en page simple, sans travail graphique.
- Le temps de réponse (`temps_ms`) est affiché sous les résultats, et `/api/stats` répond.
- Catalogue importé (générations récentes) avec au moins le socket des CPU et le type de RAM des cartes mères.
- Méthode 2 : **facultative**. Si elle n'est pas prête, la route existe mais le bouton correspondant est désactivé avec la mention « bientôt disponible », plutôt que de renvoyer des résultats non classés.

### Hors v0.1.0 (ne pas faire maintenant)

- **Aucune optimisation.** La version naïve et lisible sert de **point de départ mesuré** pour le rapport d'optimisation du 2 décembre : si on optimise maintenant, on n'aura plus rien à comparer. Pas de cache, pas d'index ajoutés « au cas où », pas de calcul vectorisé.
- Pas de dashboard graphique (Chart.js), de branding, de logo ni de mesure d'énergie.
- Pas de nouvelle fonctionnalité hors de la liste des tâches.

### « Première version, mais propre » : critères de fin

- [ ] Un clone neuf du dépôt s'installe et démarre en suivant **uniquement** le README (backend et frontend).
- [ ] `pytest` passe. Les tests de compatibilité (CPU AM5 + carte mère AM4 refusé, etc.) existent.
- [ ] Les erreurs sont gérées : une mauvaise requête renvoie une erreur 400 avec un message clair, jamais une erreur 500. Côté front, un message s'affiche si l'API ne répond pas, et un indicateur de chargement pendant l'attente.
- [ ] Pas de code mort, de `print` de débogage, de bloc commenté ni de fichier inutile. Les `# TODO` restants sont volontaires et décrivent ce qui reste à faire.
- [ ] Les noms, la structure et le contrat d'API sont cohérents partout.
- [ ] Aucune donnée, mot de passe ou fichier `.env` dans le dépôt.
- [ ] Un fichier `LICENSE` est présent (licence choisie par l'équipe, justification à écrire dans le rapport).
- [ ] Un `CHANGELOG.md` liste ce que contient la v0.1.0 et ce qui manque encore.
- [ ] Chaque fichier et chaque fonction ont leur docstring au bon format, et la doc est régénérée dans `docs/code/`.
- [ ] Les endroits améliorables sont marqués par un commentaire `# OPTI :`.
- [ ] Tout est mergé dans `main` après revue, puis taggé : `git tag v0.1.0 && git push --tags`.

## Calendrier

| Date | Rendu |
|---|---|
| 18 nov. | Dépôt Git, version v0.1.0 (ci-dessus) |
| ~2 déc. | PDF optimisation : vulgarisation pour non-développeurs, points à optimiser (vitesse, batterie), stratégies |
| 10 déc. | Branding, logo, communication intra-équipe, usage de Git et GitHub Projects |
| ~9 janv. | PDF : performances et coûts de la recommandation |
| 15 janv. | Version finale (interface finale, dashboard, méthode 2), vidéo d'utilisation, dépôt final |
| ~19 janv. | Rapport d'optimisation final ; rapport de présentation (Markdown) : public cible, argument de vente, test utilisateur |

Après le 18 : méthode 2 terminée, dashboard (temps min/max/moyen, complexité, énergie), évaluation de la pertinence (on retire une pièce d'une config réelle mise de côté et on regarde si chaque méthode la retrouve dans son top 5).

## Qualité et gestion de projet

### Ce qui est en place (à respecter dès maintenant)

- **Tests automatiques (`.github/workflows/tests.yml`)** : à chaque pull request, GitHub crée une base PostgreSQL temporaire, applique `models/schema.sql`, lance `pytest`, vérifie que la doc se génère et que le front se construit. **Une PR avec une croix rouge ne se merge pas.** Si Claude modifie le schéma, les dépendances ou la structure des dossiers, il vérifie que ce fichier fonctionne encore.
- **Modèle de pull request (`.github/pull_request_template.md`)** : chaque PR le remplit entièrement. Quand Claude rédige une description de PR, il suit ce modèle (et n'y mentionne jamais l'IA).
- **Journal des décisions (`docs/decisions.md`)** : dès qu'une décision est prise ou changée pendant le travail (choix d'algorithme, de format, de bibliothèque, abandon d'une piste), Claude **propose** une entrée `D-XX` au format du fichier. Une décision n'est jamais effacée : on en ajoute une nouvelle qui remplace l'ancienne.
- **Comptes-rendus de réunion (`docs/reunions/`)** : un fichier par réunion, à partir de `MODELE.md`.
- **`CHANGELOG.md`** : mis à jour dans chaque PR qui ajoute ou change une fonctionnalité visible (section « Non publié »).
- **Hasard reproductible** : tout code qui utilise du hasard (marche aléatoire, échantillonnage, séparation des configs de test) fixe la graine avec une constante `GRAINE = 42` définie en haut du fichier, justifiée par un commentaire `# Choix :`. Sans ça, deux mesures ne sont pas comparables et un même appel peut donner deux résultats différents devant le jury.
- **Chacun committe depuis son propre compte GitHub**, y compris le code écrit avec Claude Code : c'est le responsable de la tâche qui fait le commit. Les contributions doivent être visibles pour les 6 dans GitHub Insights.

### Roadmap des bonnes pratiques

Cocher au fur et à mesure (dans une PR, comme le reste).

**Avant le 18 novembre**
- [x] Tests automatiques sur chaque PR
- [x] Modèle de pull request
- [x] Journal des décisions, rempli avec les décisions passées
- [x] Modèle de compte-rendu de réunion
- [x] `CHANGELOG.md`
- [ ] Jalons GitHub (milestones) `v0.1.0` (18 nov.) et `v1.0.0` (15 janv.), avec chaque issue rattachée à son jalon (le sujet demande explicitement des jalons)
- [ ] Protection de la branche `main` : PR obligatoire, 1 relecture, tests verts
- [ ] Graine `GRAINE = 42` dans `services/graphe.py` (C2)
- [ ] Capture d'écran du tableau GitHub Projects (pour le rapport du 10 décembre)

**Avant le 2 décembre (rapport d'optimisation)**
- [ ] **Formateur et linter `ruff`** : `ruff format .` et `ruff check .`, ajoutés aux tests automatiques. Un seul style pour 6 personnes.
- [ ] **Script de benchmark unique `scripts/bench.py`** : toujours les mêmes scénarios de recommandation (fichier `tests/scenarios_bench.json`), N exécutions, résultats en CSV dans `docs/mesures/`. **Toutes** les mesures avant/après de `docs/optimisations.md` passent par lui, jamais par une mesure faite à la main.
- [ ] **Profiler avant d'optimiser** : `python -m cProfile -s cumtime` ou `pyinstrument` sur le scénario lent. Chaque entrée de `docs/optimisations.md` dit ce que le profileur montrait (quelle fonction prenait le plus de temps).
- [ ] **Fiche `docs/complexite.md`** : complexité de chaque méthode et de chaque étape, ce que représente chaque lettre, un exemple chiffré. Réutilisée dans tous les rapports.
- [ ] **Mini test utilisateur sur la v0.1.0** (un camarade d'une autre équipe), notes dans `docs/tests_utilisateurs/`, pour pouvoir montrer ce qui a changé grâce aux retours.
- [ ] **PostgreSQL avec Docker (`docker-compose.yml`)** : seulement si quelqu'un de l'équipe connaît Docker ; sinon, installation classique documentée dans le README.

**Avant le 10 décembre (communication)**
- [ ] Captures du tableau GitHub Projects à plusieurs dates et des jalons (avancement)
- [ ] Capture de GitHub Insights (contributions de chacun)
- [ ] Au moins un compte-rendu de réunion par semaine depuis le début du développement

**Avant le 15 janvier (version finale)**
- [ ] **Mesure de l'énergie** : `codecarbon` sur les scénarios de `scripts/bench.py` (estimation à présenter comme telle), et Lighthouse (outils de développement de Chrome) pour le front
- [ ] Test utilisateur final, prévu et décrit dans le rapport (obligatoire)
- [ ] `docs/code/` régénéré, `CHANGELOG.md` complet, tag `v1.0.0`

## Git

Une branche par tâche (`tache-08-compatibilite`), une pull request relue par quelqu'un d'un autre binôme, `Closes #numéro` dans la description de la PR, modèle de PR rempli, tests automatiques verts avant le merge. Ne jamais committer `data/`, `.env` ni `venv/`.

**Rappel : aucun `Co-Authored-By`, aucune mention de Claude ou d'une IA dans les commits et les PR.** Le réglage est aussi désactivé dans `.claude/settings.json`.
