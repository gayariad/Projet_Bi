"""Configuration pytest du WP2.

Les tests marques @pytest.mark.integration ont besoin des vraies donnees
(base PostgreSQL via URL_LECTURE dans .env, ou cache parquet complet).
Sans elles, ils sont ignores (skip) au lieu de planter.
Pour ne lancer que les tests unitaires : pytest -m "not integration".
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

RACINE = Path(__file__).resolve().parents[2]
FAMILLES = ["caracteristiques", "lieux", "usagers", "vehicules"]


def donnees_disponibles() -> bool:
    cache = RACINE / "cache"
    if all((cache / f"{famille}.parquet").exists() for famille in FAMILLES):
        return True
    load_dotenv(RACINE / ".env")
    return bool(os.environ.get("URL_LECTURE"))


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: test qui a besoin de la base PostgreSQL ou du cache parquet",
    )


def pytest_collection_modifyitems(config, items):
    if donnees_disponibles():
        return
    ignorer = pytest.mark.skip(
        reason="Donnees indisponibles : URL_LECTURE absente et cache parquet incomplet"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(ignorer)
