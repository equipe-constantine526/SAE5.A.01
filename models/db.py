"""Connexion à PostgreSQL. Tout accès à la base passe par ici.

RÈGLE : toujours des requêtes paramétrées (%s), jamais de f-string avec une valeur utilisateur.
    bon      : query("SELECT * FROM composant WHERE id = %s", (id_saisi,))
    INTERDIT : query(f"SELECT * FROM composant WHERE id = {id_saisi}")
"""
import os

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://rigmatch:rigmatch@localhost:5432/rigmatch")


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def query(sql, params=()):
    """Lecture : renvoie une liste de dictionnaires, ex. [{"id": 1, "nom": "..."}]."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def execute(sql, params=()):
    """Écriture (INSERT, UPDATE, DELETE). Le commit est fait automatiquement."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
