-- Schéma de la base RigMatch. À FINALISER à la séance à 6 (tâche 3, A1).
-- Décision ouverte : une table composant unique (ci-dessous) ou une table par type.
-- Lancer : psql -U rigmatch -d rigmatch -f models/schema.sql

CREATE TABLE IF NOT EXISTS composant (
    id            SERIAL PRIMARY KEY,
    type          TEXT NOT NULL,          -- cpu, carte_mere, ram, gpu, alim, boitier
    nom           TEXT NOT NULL,
    famille       TEXT,                   -- ex. "RTX 4070" : nœud du graphe (chantier C)
    prix          DOUBLE PRECISION,
    -- TODO A1/A2 : colonnes de caractéristiques (socket, type_ram, format, puissance, perf, ...)
    socket        TEXT,
    type_ram      TEXT,
    frequence_boost_ghz   DOUBLE PRECISION,
    tflops                DOUBLE PRECISION,
    perf          DOUBLE PRECISION                -- indice de performance sur 100 (tâche 7)
);

CREATE TABLE IF NOT EXISTS configuration (
    id        SERIAL PRIMARY KEY,
    origine   TEXT NOT NULL DEFAULT 'utilisateur',   -- 'corpus' ou 'utilisateur'
    source    TEXT,                                  -- URL de la config relevée
    validee   BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS configuration_composant (
    configuration_id INT REFERENCES configuration(id) ON DELETE CASCADE,
    composant_id     INT REFERENCES composant(id),
    PRIMARY KEY (configuration_id, composant_id)
);

-- Liens du graphe (tâche 29). Toujours a < b pour ne pas stocker un lien en double.
CREATE TABLE IF NOT EXISTS lien_graphe (
    a      INT REFERENCES composant(id),
    b      INT REFERENCES composant(id),
    poids  INT NOT NULL DEFAULT 1,
    PRIMARY KEY (a, b),
    CHECK (a < b)
);

-- Temps de réponse de chaque recommandation (tâche 21).
CREATE TABLE IF NOT EXISTS mesure (
    id        SERIAL PRIMARY KEY,
    methode   TEXT NOT NULL,          -- 'content' ou 'graph'
    temps_ms  NUMERIC NOT NULL,
    cree_le   TIMESTAMP NOT NULL DEFAULT NOW()
);
