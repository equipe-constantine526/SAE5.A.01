# Journal des versions

Les versions suivent la numérotation MAJEUR.MINEUR.CORRECTIF (Semantic Versioning) :
0.x pendant le développement, 1.0.0 pour la version finale du 15 janvier.

## [Non publié]

<!-- Ce qui sera inclus dans la prochaine version. -->

### Ajouté
- Page de saisie de la recommandation et envoi de la demande à l'API.
- Squelette frontend Vue avec Vite, affichage de la page de saisie et commandes de lancement documentées.
- Affichage des résultats après la réponse de recommandation, avec retour au formulaire.
- Réutilisation du composant partagé de recherche de composants dans la page de saisie.
- Refonte visuelle de la saisie : panneau de marque, photo fondue au-dessus du formulaire et icônes des composants sélectionnés.
- Enrichissement du catalogue enregistré dans PostgreSQL et prise en compte de la consommation des composants dans le filtre.
- Indice de performance CPU estimé à partir de la fréquence de base lorsque la fréquence boost manque dans le catalogue.
- Classement des composants sans indice de performance selon leur coût relatif au budget.
- Liste de recommandations diversifiée : une seule variante par chipset ou famille.
- Page des résultats harmonisée avec la charte RigMatch et palette centralisée en variables CSS.
- Détail du composant et configuration possédée affichés dans les résultats, avec indices arrondis à deux décimales.
- La saisie bloque comme cible un type de composant déjà indiqué comme possédé.
- Ajoute la licence MIT du code et les notices des catalogues et de la photo.

### Ajouté
- Page de saisie de la recommandation et envoi de la demande à l'API.

## [0.1.0] · 2026-11-18

Première version fonctionnelle, non optimisée (point de départ des mesures).

### Ajouté
<!-- À compléter avant le tag : ex. « Filtre de compatibilité (socket CPU / carte mère, type de RAM) » -->

### Pas encore disponible
<!-- À compléter : ex. « Méthode 2 (graphe) : route en place, recommandation pas encore classée » -->
