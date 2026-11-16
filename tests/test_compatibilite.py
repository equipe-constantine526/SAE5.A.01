"""Tests du filtre de compatibilité. Responsable : A2 (tâche 10). Lancer : pytest"""
import pytest

from services import compatibilite


PIECES = [
    {"id": 1, "type": "cpu", "socket": "AM5"},
    {"id": 2, "type": "carte_mere", "socket": "AM5", "type_ram": "DDR5"},
    {"id": 3, "type": "carte_mere", "socket": "AM4", "type_ram": "DDR4"},
    {"id": 4, "type": "ram", "type_ram": "DDR5"},
    {"id": 5, "type": "ram", "type_ram": "DDR4"},
]


@pytest.fixture(autouse=True)
def fausse_base(monkeypatch):
    """Simule les requêtes PostgreSQL avec des composants de test."""

    def query_mock(sql, params=()):
        if "WHERE id = ANY(%s)" in sql:
            return [p for p in PIECES if p["id"] in params[0]]

        resultats = [p for p in PIECES if p["type"] == params[0]]

        if "socket = %s" in sql:
            resultats = [
                p for p in resultats if p.get("socket") == params[1]
            ]

        if "type_ram = %s" in sql:
            resultats = [
                p for p in resultats if p.get("type_ram") == params[1]
            ]

        return resultats

    monkeypatch.setattr(compatibilite, "query", query_mock)


def test_cpu_am5_refuse_carte_mere_am4():
    ids = [
        c["id"]
        for c in compatibilite.compatibles([1], "carte_mere")
    ]

    assert 2 in ids
    assert 3 not in ids
    assert compatibilite.config_valide([1, 3])[0] is False