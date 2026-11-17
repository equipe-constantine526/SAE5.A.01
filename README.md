# RigMatch

Application de recommandation de composants PC : API Flask et frontend Vue. Le frontend communique uniquement avec l'API.

## Installation

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Créer la base PostgreSQL puis les tables :

```bash
createdb rigmatch
psql -d rigmatch -f models/schema.sql
```

Si votre base n'utilise pas `rigmatch:rigmatch@localhost`, définir la variable :
`DATABASE_URL=postgresql://user:motdepasse@localhost:5432/rigmatch`

## Lancer

```bash
python app.py
```

Vérifier : http://localhost:5000/api/health doit renvoyer `{"status": "ok"}`.

## Frontend

Installer Node.js, puis installer les dépendances et démarrer Vue :

```bash
cd frontend
npm install
npm run dev
```

Ouvrir http://localhost:5173. Pour utiliser les appels à l'API, laisser Flask démarré dans un autre terminal.

## Organisation

```
app.py            point d'entrée, enregistre les routes
controllers/      les routes : lisent la requête, appellent un service, renvoient du JSON. AUCUN calcul ici.
services/         toute la logique : compatibilité, méthode 1, méthode 2, configs, mesures
models/           connexion à la base (db.py) et schéma (schema.sql)
scripts/          import et enrichissement, lancés une seule fois
tests/            pytest
```

| Fichier | Responsable |
|---|---|
| services/compatibilite.py, controllers/composants.py | A2 |
| scripts/import_catalogue.py, models/schema.sql | A1 |
| scripts/enrichissement.py | A2 |
| services/score_contenu.py | B1 |
| controllers/recommandation.py, services/mesures.py, controllers/stats.py | B2 |
| services/configs.py, controllers/configs.py, scripts/import_corpus.py | C1 |
| services/graphe.py | C2 |

## Contrat d'API

| Route | Entrée | Sortie |
|---|---|---|
| `GET /api/health` | | `{"status": "ok"}` |
| `GET /api/composants?type=gpu&q=4070` | | `[{"id", "nom", "prix"}]` |
| `POST /api/recommend/content` | `{"composants": [ids], "budget", "usage", "type_cherche"}` | `{"resultats": [{"id", "nom", "prix", "score"}], "temps_ms"}` |
| `POST /api/recommend/graph` | même entrée | même sortie |
| `POST /api/configs` | `{"composants": [ids]}` | 201 `{"id"}` ou 400 `{"erreur"}` |
| `GET /api/stats` | | `[{"methode", "min", "max", "moyenne", "nb"}]` |

Toute modification de ce contrat se décide en équipe et se note ici.

## Règles

- Une branche par tâche, une pull request relue par quelqu'un d'un autre binôme.
- Requêtes SQL toujours paramétrées (`%s`), jamais de f-string avec une valeur utilisateur.
- Le filtre de compatibilité tourne côté backend, jamais seulement dans le front.
- Les fichiers de données vont dans `data/` (ignoré par Git).
