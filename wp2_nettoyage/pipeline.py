"""Pipeline de nettoyage : applique les ÃƒÂ©tapes de ORDRE, dans l'ordre, aux tables brutes.

Chaque ÃƒÂ©tape est un module etapes/eNNN_nom.py qui expose appliquer(t: dict) -> dict.
Pour ajouter une ÃƒÂ©tape : crÃƒÂ©er le fichier, puis ajouter son nom dans ORDRE.
"""
import importlib

from commun.recuperer_donnees import charger_tout

ORDRE = [
    "e100_exemple",
    "e110_harmonisation",
    "e115_typage",
    "e120_valeurs_manquantes",
    "e150_lieu_principal",
]


def donnees_propres(rafraichir=False):
    """Tables brutes (charger_tout) passÃƒÂ©es par toutes les ÃƒÂ©tapes de ORDRE."""
    t = charger_tout(rafraichir=rafraichir)
    for nom in ORDRE:
        etape = importlib.import_module(f"wp2_nettoyage.etapes.{nom}")
        t = etape.appliquer(t)
    return t
