"""WP2 - R004 : normalisation des marqueurs manquants de lieux.v2.

Proposition en attente de validation métier.
Ne modifie ni PostgreSQL ni les DataFrames d'entrée.
"""

import pandas as pd


def appliquer(t: dict) -> dict:
    resultat = dict(t)

    lieux = t["lieux"].copy()

    valeurs = lieux["v2"].astype("string").str.strip()

    marqueurs = valeurs.str.lower().isin(
        ["n/a", "null"]
    ).fillna(False)

    lieux["v2"] = valeurs.mask(marqueurs, pd.NA)

    resultat["lieux"] = lieux

    return resultat
