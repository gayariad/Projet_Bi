"""Pipeline de nettoyage : applique les étapes de ORDRE, dans l'ordre, aux tables brutes.

Chaque étape est un module etapes/eNNN_nom.py qui expose appliquer(t: dict) -> dict.
Pour ajouter une étape : créer le fichier, puis ajouter son nom dans ORDRE.
"""
import importlib

from commun.recuperer_donnees import charger_tout

ORDRE = [
    "e100_exemple",
]


def donnees_propres(rafraichir=False):
    """Tables brutes (charger_tout) passées par toutes les étapes de ORDRE."""
    t = charger_tout(rafraichir=rafraichir)
    for nom in ORDRE:
        etape = importlib.import_module(f"wp2_nettoyage.etapes.{nom}")
        t = etape.appliquer(t)
    return t
