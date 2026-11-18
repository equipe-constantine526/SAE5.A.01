# Journal des décisions

Chaque décision importante du projet est notée ici : ce qu'on a décidé, ce qu'on a écarté, et pourquoi.
Une décision n'est jamais effacée : si on change d'avis, on ajoute une nouvelle entrée qui remplace l'ancienne.

Modèle :

```markdown
## D-XX · Titre court

- **Date :** AAAA-MM-JJ
- **Décision :** ce qu'on fait.
- **Alternatives écartées :** ce qu'on aurait pu faire.
- **Pourquoi :** les raisons.
- **Conséquences :** ce que ça implique pour la suite (ce qu'on gagne, ce qu'on perd).
```

---

## D-01 · Thème : recommandation de composants PC compatibles

- **Date :** octobre 2026 (description rendue le 8 octobre)
- **Décision :** l'application aide à monter ou améliorer un PC en recommandant des composants compatibles avec ceux que l'utilisateur possède, selon son budget et son usage.
- **Pourquoi :** besoin réel (peur d'acheter des pièces incompatibles ou trop chères), données publiques disponibles, et la compatibilité donne un critère objectif pour vérifier les recommandations.
- **Conséquences :** il faut un filtre de compatibilité fiable, donc des données techniques complètes (socket, type de RAM, consommation).

## D-02 · Pas de notes données par les utilisateurs

- **Date :** octobre 2026
- **Décision :** aucune méthode ne repose sur des notes d'utilisateurs.
- **Alternatives écartées :** filtrage collaboratif classique à partir de notes.
- **Pourquoi :** une note dit si une pièce est bonne, pas si elle va avec les autres. Et aucun jeu de données public de notes de composants n'existe : il aurait fallu les inventer, ce qui aurait faussé la comparaison.
- **Conséquences :** la seconde méthode s'appuie sur des configurations réellement montées.

## D-03 · Des fichiers de données, pas d'API extérieure

- **Date :** octobre 2026
- **Décision :** le catalogue (`docyx/pc-part-dataset`, licence MIT) et les données GPU (`rightnow-gpu-database`) sont téléchargés une fois puis importés dans PostgreSQL.
- **Alternatives écartées :** interroger un site en direct (PCPartPicker n'a pas d'API publique, et son scraping est contraire à ses conditions).
- **Pourquoi :** l'application ne dépend d'aucun site extérieur, la démonstration ne peut pas tomber en panne à cause d'un autre service, et les données restent stables pour les mesures.
- **Conséquences :** les prix ne sont pas à jour en temps réel ; certaines informations manquantes sont complétées par nos propres tables (socket, type de RAM).

## D-04 · Un filtre de compatibilité commun, avant les deux méthodes

- **Date :** octobre 2026
- **Décision :** un seul filtre élimine les pièces incompatibles ; les deux méthodes ne font que classer les pièces restantes.
- **Pourquoi :** aucune méthode ne peut recommander une pièce incompatible, et elles choisissent parmi exactement les mêmes candidats : la comparaison est équitable.
- **Conséquences :** le filtre est le point dont tout dépend ; il doit être testé (`tests/test_compatibilite.py`).

## D-05 · Pas de comptes utilisateurs ni d'espace administrateur

- **Date :** octobre 2026, validé par le retour de l'enseignant
- **Décision :** pas de comptes ; la saisie de l'utilisateur est gardée dans le localStorage de son navigateur. L'équipe gère les données directement en base.
- **Alternatives écartées :** comptes avec mot de passe, interface admin.
- **Pourquoi :** aucune des deux méthodes n'a besoin de savoir qui est l'utilisateur ; le sujet met en garde contre la surcharge de fonctionnalités, et une gestion des comptes ajoute des risques de sécurité sans servir la comparaison.
- **Conséquences :** la configuration ne suit pas l'utilisateur d'un appareil à l'autre ; n'importe qui peut ajouter une configuration (limité par le filtre et la détection des doublons).

## D-06 · Stack : Flask, Vue.js, PostgreSQL

- **Date :** octobre 2026, validée par le retour de l'enseignant
- **Décision :** backend Python avec Flask, frontend Vue.js séparé, base PostgreSQL.
- **Pourquoi :** Python est adapté à la manipulation de données (pandas) ; Vue permet un front découplé qui ne parle qu'à l'API ; les données sont très relationnelles (socket, type de RAM), et la compatibilité se traduit en requêtes SQL.

## D-07 · Seconde méthode : recommandation par graphe (Personalized PageRank)

- **Date :** novembre 2026, après le retour de l'enseignant sur la description
- **Décision :** la seconde méthode représente les composants comme un graphe (lien entre deux pièces montées ensemble, pondéré par le nombre de configurations) et recommande par marche aléatoire avec retour au point de départ (Personalized PageRank).
- **Alternatives écartées :** comptage simple des pièces souvent choisies ensemble (notre version initiale) ; regroupement des configurations (clustering).
- **Pourquoi :** l'enseignant a jugé nos deux méthodes initiales trop proches (« deux approches heuristiques ») et a suggéré un graphe. Le graphe réutilise les mêmes données, trouve des liens indirects que le comptage ne voit pas, et offre une vraie matière d'optimisation (itérations, matrice creuse).
- **Conséquences :** les deux méthodes sont de types différents : règles sur les fiches techniques d'un côté, choix réels des utilisateurs sous forme de graphe de l'autre.

## D-08 · Nœuds du graphe : des familles de pièces

- **Date :** novembre 2026
- **Décision :** un nœud du graphe correspond à une famille (ex. « RTX 4070 »), pas à une référence exacte (ex. « MSI RTX 4070 Ventus 2X »).
- **Pourquoi :** avec environ 300 configurations, presque aucune référence exacte n'apparaîtrait deux fois : le graphe serait trop vide pour recommander quoi que ce soit.

## D-09 · Suivi des tâches avec GitHub Projects

- **Date :** 2026-11-13
- **Décision :** tableau GitHub Projects, une issue par tâche, chaque pull request liée à son issue.
- **Alternatives écartées :** Jira, Trello.
- **Pourquoi :** pas de nouvel outil à apprendre, tout est au même endroit que le code, et une tâche se ferme automatiquement quand sa PR est mergée.

## D-10 · Aucune optimisation avant la v0.1.0

- **Date :** 2026-11-14
- **Décision :** la v0.1.0 (18 novembre) est volontairement naïve et lisible ; les endroits améliorables sont seulement repérés par des commentaires `# OPTI :`.
- **Pourquoi :** cette version sert de point de départ mesuré. Chaque optimisation sera comparée à elle, avec des chiffres, dans `docs/optimisations.md`.

## D-12 · Une seule table `composant`, colonnes de calcul en `DOUBLE PRECISION`

- **Date :** 2026-11-14 (à valider par A1, responsable du schéma)
- **Décision :** les 6 types de pièces sont dans une seule table `composant`, avec des colonnes propres à chaque type (vides pour les autres). Seules les colonnes utilisées par le filtre, le score ou le calcul de performance sont ajoutées. Les nombres servant aux calculs (prix, fréquence, TFLOPS, perf) sont en `DOUBLE PRECISION`.
- **Alternatives écartées :** une table par type ; `NUMERIC` ou `REAL` pour les nombres.
- **Pourquoi :** une seule table donne un identifiant unique par pièce, ce qui simplifie le graphe et le filtre. `DOUBLE PRECISION` est le même format que le `float` de Python : `NUMERIC` renvoie des `Decimal`, incompatibles avec les calculs en `float`, et `REAL` est moins précis sans gain utile à notre échelle.
- **Conséquences :** beaucoup de cases vides, documentées par des commentaires dans `schema.sql` ; une colonne n'est ajoutée que si une règle s'en sert.

## D-11 · Sécurité limitée aux réflexes de base

- **Date :** novembre 2026, après le retour de l'enseignant
- **Décision :** requêtes SQL paramétrées et filtre de compatibilité côté backend, rien de plus pour l'instant.
- **Pourquoi :** l'enseignant a précisé que la sécurité n'est pas ce qui est évalué dans la SAÉ.

## D-13 · Lancer le frontend Vue avec Vite

- **Date :** 2026-11-17
- **Décision :** utiliser Vite pour lancer et construire le frontend Vue ; `App.vue` affiche directement la page `Saisie.vue` comme première page de l'application.
- **Alternatives écartées :** ajouter un routeur et une page d'accueil avant que les autres pages soient intégrées.
- **Pourquoi :** le formulaire de saisie est la page déjà disponible ; le démarrer directement permet de vérifier le frontend sans ajouter de navigation hors du périmètre du squelette.
- **Conséquences :** `npm run dev` démarre l'interface sur le port 5173 et `npm run build` vérifie sa compilation. Une navigation entre plusieurs pages pourra être ajoutée quand les vues seront prêtes.

## D-14 · Relier la saisie à la page de résultats dans `App.vue`

- **Date :** 2026-11-17
- **Décision :** `App.vue` écoute l'événement `recommandation` de `Saisie.vue`, transmet la liste reçue à `Resultats.vue`, et permet de revenir au formulaire.
- **Alternatives écartées :** ajouter Vue Router pour ce passage entre les deux vues.
- **Pourquoi :** le parcours actuel ne comporte que la saisie et les résultats ; le composant racine peut gérer ce changement d'affichage sans ajouter de dépendance.
- **Conséquences :** les choix du formulaire restent restaurables depuis `localStorage` après le retour. Si le nombre de vues augmente, il faudra réévaluer le besoin d'un routeur.

## D-15 · Réutiliser `RechercheComposant.vue` dans la saisie

- **Date :** 2026-11-17
- **Décision :** la page `Saisie.vue` délègue l'autocomplétion à `RechercheComposant.vue` et conserve la liste des pièces sélectionnées.
- **Alternatives écartées :** maintenir une deuxième recherche et une deuxième liste de suggestions dans la page de saisie.
- **Pourquoi :** le composant partagé gère déjà le délai de recherche, les suggestions, l'annulation des anciennes requêtes et la navigation au clavier.
- **Conséquences :** `Saisie.vue` reçoit la pièce via l'événement `select`, lui associe le type choisi et évite les doublons avant de l'ajouter à la configuration.

## D-16 · Estimer la performance CPU si la fréquence boost manque

- **Date :** 2026-11-18
- **Décision :** utiliser la fréquence de base pour calculer un indice CPU lorsque le catalogue ne fournit pas de fréquence boost. La ligne conserve une source qui indique que l'indice est estimé.
- **Alternative écartée :** laisser l'indice vide, ce qui rend le CPU neutre dans la règle d'équilibre CPU/GPU.
- **Pourquoi :** le catalogue contient par exemple le Celeron G6900 avec 2 cœurs et une fréquence de base de 3,4 GHz, mais sans fréquence boost ; une valeur basse et signalée est plus utile qu'une absence totale d'indice.
- **Conséquences :** cet indice n'est pas directement comparable à un indice calculé avec la fréquence boost ; il reste une estimation tant que la source ne fournit pas cette donnée.

## D-17 · Départager RAM, cartes mères, alimentations et boîtiers par le prix

- **Date :** 2026-11-18
- **Décision :** pour la RAM, les cartes mères, les alimentations et les boîtiers, calculer la règle budget comme `budget_piece / (budget_piece + prix)`, ce qui favorise une pièce moins coûteuse tout en gardant une note entre 0 et 1. Les CPU et GPU conservent leur règle actuelle.
- **Alternative écartée :** garder la note neutre `0.5`, qui donne le même score à toutes les pièces et laisse leur ordre dépendre de celui de PostgreSQL.
- **Pourquoi :** ces types n'ont pas d'indice de performance dans le schéma ; le prix est le seul critère numérique commun disponible.
- **Conséquences :** le classement est plus explicable, mais une RAM peu chère peut avoir une faible capacité. Il faudra ajouter capacité et vitesse à la collecte avant de présenter ce classement comme une comparaison technique.

## D-18 · Limiter les variantes d'un chipset dans les recommandations

- **Date :** 2026-11-18
- **Décision :** ne conserver que le meilleur résultat par chipset (ou famille si le chipset manque) dans la liste finale.
- **Alternative écartée :** afficher plusieurs références presque identiques d'une même puce, ce qui masque les autres choix disponibles.
- **Pourquoi :** le catalogue contient de nombreuses variantes d'un GPU ; dans un essai, 7 des 10 premiers résultats étaient des RX 9060 XT.
- **Conséquences :** la liste montre des composants plus différents, mais peut contenir moins de 10 résultats si le catalogue offre moins de 10 chipsets compatibles.
