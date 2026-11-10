"""Pipeline WP2 - Nettoyage des donnees BAAC 2019-2024."""

import importlib

from commun.recuperer_donnees import charger_tout

ORDRE = [
    "e100_exemple",
    "e110_harmonisation",
    "e115_typage",
    "e120_valeurs_manquantes",
]


def donnees_propres(rafraichir=False):
    """Charge et nettoie les quatre tables BAAC."""
    t = charger_tout(rafraichir=rafraichir)

    for nom in ORDRE:
        module = importlib.import_module(
            f"wp2_nettoyage.etapes.{nom}"
        )
        t = module.appliquer(t)

    return t
