-- Schéma de la base RigMatch.
-- Responsable : A1 · Tâche 3 (décision D-12 dans docs/decisions.md)
--
-- Lancer : psql -d rigmatch -f models/schema.sql
-- Le fichier peut être relancé sans risque : chaque table n'est créée que si elle n'existe pas.
--
-- Qui remplit quoi :
--   composant                : scripts/import_catalogue.py (A1), puis scripts/enrichissement.py (A2)
--   configuration, configuration_composant : scripts/import_corpus.py et services/configs.py (C1)
--   lien_graphe              : services/graphe.py (C2)
--   mesure                   : services/mesures.py (B2)


-- ---------------------------------------------------------------------------
-- composant : toutes les pièces du catalogue, les 6 types dans la même table.
-- ---------------------------------------------------------------------------
-- Choix : une seule table pour les 6 types plutôt qu'une table par type (D-12, C-10).
-- Une seule table donne un identifiant unique à chaque pièce : une configuration ou un
-- lien du graphe pointe vers composant(id) sans savoir de quel type est la pièce.
-- Avec une table par type, il faudrait 6 clés étrangères possibles dans
-- configuration_composant. En contrepartie, beaucoup de cases sont vides : un CPU n'a
-- pas de puissance d'alim. Chaque colonne indique ci-dessous les types qui la remplissent.
--
-- Choix : on n'ajoute une colonne que si le filtre de compatibilité, le score de la
-- méthode 1 ou le calcul de perf s'en sert. Le jeu de données a d'autres champs
-- (couleur, latence de la RAM, nombre de baies...) qu'on ne garde pas : ils
-- alourdiraient la table sans servir à aucune règle.
--
-- Choix : DOUBLE PRECISION pour les nombres servant aux calculs, plutôt que NUMERIC
-- (D-12, C-07). C'est le même format que le float de Python ; NUMERIC renvoie des
-- Decimal, qui ne se mélangent pas avec des float dans les calculs du score.
CREATE TABLE IF NOT EXISTS composant (
    id                 SERIAL PRIMARY KEY,
    type               TEXT NOT NULL
                       CHECK (type IN ('cpu', 'carte_mere', 'ram', 'gpu', 'alim', 'boitier')),
    nom                TEXT NOT NULL,             -- ex. 'AMD Ryzen 5 7600'
    famille            TEXT,                      -- nœud du graphe (D-08), ex. 'RTX 4070'. Rempli par C1/C2
    prix               DOUBLE PRECISION,          -- en dollars, comme le jeu de données. NULL si inconnu
    perf               DOUBLE PRECISION,          -- cpu, gpu : indice sur 100 dans son type (tâche 7)

    -- Processeur (cpu)
    microarchitecture  TEXT,                      -- cpu : ex. 'Zen 4'. Sert à retrouver le socket (tâche 4)
    nb_coeurs          INT,                       -- cpu : ex. 6
    frequence_boost    DOUBLE PRECISION,          -- cpu : en GHz, ex. 5.1

    -- Compatibilité
    socket             TEXT,                      -- cpu, carte_mere : ex. 'AM5'. cpu rempli par A2 (tâche 4)
    type_ram           TEXT                       -- carte_mere, ram : 'DDR4' ou 'DDR5'
                       CHECK (type_ram IN ('DDR4', 'DDR5')),
    type_ram_verifie   BOOLEAN,                   -- carte_mere : FALSE si le type est supposé (LGA1700 sans « DDR4 » dans le nom, tâche 5)
    format             TEXT,                      -- carte_mere : ex. 'Micro ATX' ; boitier : ex. 'ATX Mid Tower'

    -- Carte graphique (gpu)
    chipset            TEXT,                      -- gpu : ex. 'GeForce RTX 4070'. Clé de la jointure avec la base GPU (tâche 6)
    tflops             DOUBLE PRECISION,          -- gpu : puissance de calcul FP32, ex. 29.15 (tâche 7)
    alim_conseillee_w  INT,                       -- gpu : alim conseillée en watts, ex. 550 (tâche 6)

    -- Consommation et alimentation
    conso_w            INT,                       -- cpu, gpu : consommation (TDP) en watts. gpu rempli par A2 (tâche 6)
    puissance_w        INT,                       -- alim : puissance en watts, ex. 750

    -- Origine des valeurs que le jeu de données ne donne pas (règle : chaque valeur ajoutée garde sa source)
    source             TEXT                       -- ex. 'socket : data/microarch_socket.csv ; tflops : techpowerup'
);

-- OPTI (P-01) : aucun index sur les colonnes filtrées
--   Maintenant : le filtre de compatibilité cherche par type et socket (ou type_ram) ;
--                sans index, PostgreSQL lit toute la table à chaque requête. O(n),
--                n = nombre de lignes de composant.
--   Pourquoi c'est améliorable : on lit des milliers de lignes pour n'en garder que
--                quelques centaines.
--   Piste : CREATE INDEX ON composant (type, socket); et (type, type_ram).
--   Gain attendu : à mesurer (EXPLAIN ANALYZE sur la requête du filtre, avant et après).


-- ---------------------------------------------------------------------------
-- configuration : une configuration réelle (corpus) ou ajoutée par un utilisateur.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS configuration (
    id        SERIAL PRIMARY KEY,
    origine   TEXT NOT NULL DEFAULT 'utilisateur'
              CHECK (origine IN ('corpus', 'utilisateur')),
    source    TEXT,                                  -- URL de la config relevée (corpus)
    validee   BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Table de liaison : quelles pièces composent quelle configuration.
-- Choix : ON DELETE CASCADE sur la configuration (supprimer une config supprime ses
-- lignes ici), mais pas sur le composant : on refuse de supprimer une pièce utilisée
-- dans une config, sinon la config perdrait une pièce sans prévenir.
CREATE TABLE IF NOT EXISTS configuration_composant (
    configuration_id INT REFERENCES configuration(id) ON DELETE CASCADE,
    composant_id     INT REFERENCES composant(id),
    PRIMARY KEY (configuration_id, composant_id)
);


-- ---------------------------------------------------------------------------
-- lien_graphe : liens de la méthode 2 (tâche 29).
-- ---------------------------------------------------------------------------
-- Toujours a < b : la paire (412, 1580) n'est stockée qu'une fois, jamais aussi en (1580, 412).
CREATE TABLE IF NOT EXISTS lien_graphe (
    a      INT REFERENCES composant(id),
    b      INT REFERENCES composant(id),
    poids  INT NOT NULL DEFAULT 1,                   -- nombre de configs où a et b apparaissent ensemble
    PRIMARY KEY (a, b),
    CHECK (a < b)
);


-- ---------------------------------------------------------------------------
-- mesure : temps de réponse de chaque recommandation (tâche 21).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mesure (
    id        SERIAL PRIMARY KEY,
    methode   TEXT NOT NULL CHECK (methode IN ('content', 'graph')),
    temps_ms  DOUBLE PRECISION NOT NULL,             -- DOUBLE PRECISION pour la même raison que plus haut (C-07)
    cree_le   TIMESTAMP NOT NULL DEFAULT NOW()
);
