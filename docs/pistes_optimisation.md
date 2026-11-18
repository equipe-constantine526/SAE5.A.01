# Choix d'optimisation et pistes connues

Ce document a deux parties :
1. **Les choix déjà faits** qui ont un effet sur la performance, avec leur justification.
2. **Les points à optimiser dont nous sommes conscients** (pistes `P-XX`), avec ce qu'on compte faire et comment on le mesurera.

Il sert de base au rapport du 2 décembre (points à optimiser, points pour économiser la batterie, stratégies).
Les optimisations **réellement faites et mesurées** vont dans `docs/optimisations.md` (entrées `O-XX`).

Dans le code, chaque piste est repérée par un commentaire qui porte son numéro : `# OPTI (P-02) :`.
Pour tout lister : `grep -rn "OPTI" --include=*.py --include=*.vue --include=*.js --include=*.sql . | grep -v node_modules`

**Règle : aucun chiffre de gain n'est écrit ici tant qu'il n'a pas été mesuré.**

---

## 1. Choix déjà faits

| # | Choix | Effet sur la performance | Contrepartie |
|---|---|---|---|
| C-01 | **Seulement les générations récentes** dans le catalogue (61 000 pièces au départ, quelques milliers après filtrage) | Moins de lignes à lire, à filtrer et à classer à chaque requête | Les configurations anciennes ne sont pas gérées |
| C-02 | **Filtre de compatibilité appliqué avant les deux méthodes** | Les méthodes ne classent que les candidats compatibles : le n de leur complexité est plus petit | Aucune, c'est aussi ce qui rend la comparaison équitable |
| C-03 | **Indice de performance (`perf`) calculé une fois à l'import** et stocké en base | À la requête, une simple lecture au lieu d'un calcul : le coût passe du moment de la requête au moment de l'import | Si la formule change, il faut relancer l'import |
| C-04 | **Liens du graphe stockés en base** (table `lien_graphe`) | Pas besoin de reparcourir toutes les configurations à chaque recommandation | Il faut tenir les liens à jour à chaque ajout de config |
| C-05 | **Mise à jour incrémentale des liens** : un ajout de config n'ajoute que ses propres paires | k(k−1)/2 paires (15 pour 6 pièces) au lieu de recalculer tout le graphe, O(c × k²) | Supprimer une config demande de retirer ses paires à la main |
| C-06 | **Nœuds du graphe = familles de pièces** (« RTX 4070 »), pas les références exactes | Graphe beaucoup plus petit et plus dense : moins de nœuds à parcourir, plus de liens utiles | On ne distingue plus deux modèles de la même famille |
| C-07 | **`DOUBLE PRECISION` pour les colonnes de calcul** (prix, fréquence, TFLOPS, perf) plutôt que `NUMERIC` | Le même format que le `float` de Python : pas de conversion, calculs directs. `NUMERIC` renvoie des `Decimal`, plus lents et incompatibles avec les `float` | Valeurs approximatives au-delà de 15 chiffres significatifs : sans importance ici |
| C-08 | **Données locales**, pas d'appel à une API extérieure | Pas d'attente réseau vers un autre site pendant une recommandation | Prix pas à jour en temps réel |
| C-09 | **Recherche d'autocomplétion limitée à 20 résultats** (`LIMIT 20`) | Réponse légère, quelle que soit la taille du catalogue | L'utilisateur doit taper un texte assez précis |
| C-10 | **Une seule table `composant`** pour les 6 types | Un seul identifiant par pièce : le graphe et le filtre travaillent sur une seule table, sans jointure entre tables de types | Beaucoup de colonnes vides (un CPU n'a pas de puissance d'alim) |

---

## 2. Points à optimiser (pistes)

Priorité : **haute** = probablement visible dans les mesures, **moyenne** = gain probable mais faible à notre échelle, **basse** = surtout intéressant à expliquer.
Type : **vitesse** (temps de réponse) ou **énergie** (batterie, réseau, ressources).

### Base de données

#### P-01 · Index sur les colonnes filtrées
- **Maintenant :** aucun index ; PostgreSQL lit toute la table à chaque filtre (`Seq Scan`). O(n), n = nombre de composants.
- **Piste :** `CREATE INDEX ON composant (type, socket);` et `(type, type_ram)`.
- **Mesure :** `EXPLAIN ANALYZE` sur la requête du filtre, et temps de `/api/recommend/content`, **sur le catalogue filtré et sur le catalogue complet** (61 000 pièces) pour montrer l'effet de la taille.
- **Priorité :** moyenne (probablement invisible sur quelques milliers de lignes, visible sur le catalogue complet) · **Type :** vitesse
- **Statut :** à faire

#### P-02 · Une requête par pièce de l'utilisateur (problème « N+1 »)
- **Maintenant :** si les pièces de l'utilisateur sont lues une par une, 6 pièces = 6 allers-retours avec la base.
- **Piste :** une seule requête : `SELECT ... WHERE id = ANY(%s)`.
- **Mesure :** nombre de requêtes et temps de la fonction, avant/après.
- **Priorité :** haute · **Type :** vitesse
- **Statut :** à vérifier dans `services/compatibilite.py`

#### P-03 · `SELECT *` au lieu des colonnes utiles
- **Maintenant :** on récupère toutes les colonnes de chaque pièce, puis on renvoie de gros objets au front.
- **Piste :** ne sélectionner que les colonnes nécessaires à chaque usage ; alléger la réponse JSON.
- **Mesure :** taille de la réponse JSON (octets) et temps de réponse.
- **Priorité :** moyenne · **Type :** vitesse et énergie
- **Statut :** à faire

#### P-04 · Filtrer en SQL plutôt qu'en Python
- **Maintenant (si c'est le cas) :** on charge toutes les pièces d'un type puis on garde les compatibles en Python.
- **Piste :** mettre toutes les conditions de compatibilité dans le `WHERE`.
- **Mesure :** temps du filtre, nombre de lignes transférées.
- **Priorité :** haute · **Type :** vitesse
- **Statut :** à vérifier

#### P-05 · Une nouvelle connexion à la base à chaque requête SQL
- **Maintenant :** `models/db.py` ouvre et ferme une connexion PostgreSQL à **chaque** appel de `query()` ou `execute()`. Une recommandation qui fait plusieurs requêtes paie plusieurs fois le coût d'ouverture.
- **Piste :** un « pool » de connexions ouvertes une fois et réutilisées (`psycopg_pool`).
- **Mesure :** temps de `/api/recommend/content` avant/après, avec le script de benchmark.
- **Priorité :** haute · **Type :** vitesse
- **Statut :** à faire

### Méthode 1 (score sur les fiches techniques)

#### P-06 · Indice de performance CPU approximatif (précision)
- **Maintenant :** `perf = nb_coeurs × fréquence boost`. Ignore l'architecture : deux processeurs de 8 cœurs de générations différentes ont presque le même score.
- **Piste :** remplacer par des scores de benchmark réels (Cinebench, PassMark) pour les CPU récents.
- **Mesure :** pertinence avec le test « on retire une pièce d'une config réelle, la méthode la retrouve-t-elle dans son top 5 ? », avant/après.
- **Priorité :** moyenne · **Type :** précision (la compétence Optimisation porte aussi sur la précision)
- **Statut :** à faire après le 18

#### P-07 · Normalisation recalculée à chaque requête
- **Maintenant :** pour ramener perf/prix entre 0 et 1, on cherche le maximum parmi les candidats à chaque requête : un parcours en plus.
- **Piste :** à comparer avec une normalisation globale calculée à l'import (attention : ça change le sens du score, à discuter).
- **Mesure :** temps du classement.
- **Priorité :** basse · **Type :** vitesse
- **Statut :** à discuter

#### P-08 · Enchaînement pour un PC complet
- **Maintenant :** 6 types recommandés l'un après l'autre = 6 fois filtre + classement, avec leurs requêtes.
- **Piste :** regrouper les lectures en base (charger une fois toutes les pièces utiles), réutiliser les résultats intermédiaires.
- **Mesure :** temps d'un PC complet, nombre de requêtes.
- **Priorité :** moyenne · **Type :** vitesse
- **Statut :** à faire quand l'enchaînement existe

### Méthode 2 (graphe)

#### P-09 · Nombre d'itérations de la marche aléatoire
- **Maintenant :** nombre d'itérations fixe (ou paramètres par défaut de networkx).
- **Piste :** s'arrêter dès que le classement des premières pièces ne bouge plus (convergence).
- **Mesure :** temps et nombre d'itérations, et vérifier que le top 5 reste le même.
- **Priorité :** haute · **Type :** vitesse et énergie
- **Statut :** à faire quand la méthode 2 existe

#### P-10 · Représentation du graphe
- **Maintenant :** graphe networkx (objets Python, pratique mais lourd).
- **Piste :** notre propre implémentation avec une **matrice creuse** (on ne stocke que les liens qui existent).
- **Mesure :** temps et mémoire utilisée.
- **Priorité :** haute · **Type :** vitesse et énergie
- **Statut :** à faire après le prototype

#### P-11 · Graphe relu en base à chaque recommandation
- **Maintenant :** chaque recommandation relit la table `lien_graphe`.
- **Piste :** charger le graphe en mémoire au démarrage du serveur, le mettre à jour quand une config est ajoutée.
- **Mesure :** temps de `/api/recommend/graph`.
- **Priorité :** haute · **Type :** vitesse
- **Statut :** à faire

### Application en général

#### P-12 · Pas de cache des recommandations
- **Maintenant :** une même demande est recalculée entièrement à chaque fois.
- **Piste :** garder en mémoire les résultats des demandes récentes ; à invalider pour la méthode 2 quand une config est ajoutée.
- **Mesure :** temps d'une demande répétée.
- **Priorité :** moyenne · **Type :** vitesse et énergie
- **Statut :** à faire, et à justifier (le cache fausse les mesures de temps : il faut le désactiver pendant les benchmarks)

#### P-13 · Une écriture en base pour chaque mesure de temps
- **Maintenant :** chaque recommandation écrit une ligne dans la table `mesure` : une requête de plus, à chaque fois.
- **Piste :** regrouper les mesures en mémoire et les écrire par lots.
- **Mesure :** temps de réponse avec et sans enregistrement.
- **Priorité :** basse · **Type :** vitesse
- **Statut :** à discuter (la mesure ne doit pas trop ralentir ce qu'elle mesure)

### Frontend

#### P-14 · Une requête d'autocomplétion par lettre tapée
- **Maintenant :** taper « 4070 » envoie 4 requêtes à l'API.
- **Piste :** attendre 300 ms sans frappe avant d'appeler l'API (debounce).
- **Mesure :** nombre de requêtes pour une même saisie (onglet Réseau du navigateur).
- **Priorité :** haute · **Type :** énergie
- **Statut :** à faire dans `RechercheComposant.vue`

#### P-15 · Taille et compression des réponses
- **Maintenant :** réponses JSON non compressées, avec le détail du score pour chaque pièce.
- **Piste :** compression gzip côté Flask, détail du score seulement pour les pièces affichées.
- **Mesure :** taille transférée (onglet Réseau), score Lighthouse.
- **Priorité :** basse · **Type :** énergie
- **Statut :** à faire

#### P-16 · Mises à jour SQL de l'enrichissement
- **Maintenant :** le script exécute un `UPDATE` séparé pour chaque composant enrichi.
- **Piste :** préparer les valeurs puis utiliser `executemany` une fois par type de composant.
- **Mesure :** durée totale de `python -m scripts.enrichissement`.
- **Priorité :** basse (script lancé après l'import, pas pendant une recommandation) · **Type :** vitesse
- **Statut :** à mesurer après le 18

---

## 3. Comment on mesure

- **Temps :** script `scripts/bench.py` (mêmes scénarios, N exécutions, résultats en CSV dans `docs/mesures/`). Jamais de mesure faite à la main.
- **Où passe le temps :** `python -m cProfile -s cumtime` ou `pyinstrument`, avant de choisir quoi optimiser.
- **Base de données :** `EXPLAIN ANALYZE` devant la requête.
- **Énergie :** `codecarbon` (estimation, à présenter comme telle) ; Lighthouse et onglet Réseau pour le front.
- **Précision :** test « on retire une pièce » (taux de pièces retrouvées dans le top 5), sur des configurations mises de côté.
- **Reproductibilité :** graine fixée (`GRAINE = 42`) pour tout ce qui est aléatoire, même machine pour l'avant et l'après.
