"""Exemple WP5 : nombre d'usagers par gravité et par année.

Lancement depuis la racine du repo : python -m wp5_analyses.exemple
"""
import pandas as pd

from wp2_nettoyage.pipeline import donnees_propres

GRAVITE = {"1": "indemne", "2": "tué", "3": "blessé hospitalisé", "4": "blessé léger"}

usagers = donnees_propres()["usagers"]
gravite = usagers["grav"].str.strip().map(GRAVITE).fillna("non renseigné").rename("gravité")
tableau = pd.crosstab(gravite, usagers["annee"], margins=True, margins_name="total")
print(tableau)
