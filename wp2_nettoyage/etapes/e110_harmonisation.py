"""WP2-06 : harmonisation technique des données BAAC.

Cette étape ne modifie pas les données brutes PostgreSQL.
Les transformations métier sont traitées dans des étapes séparées.
"""

def appliquer(t: dict) -> dict:
    resultat = dict(t)

    c = t["caracteristiques"].copy()

    # Uniformiser le séparateur décimal des coordonnées.
    # Ne pas supprimer les valeurs manquantes ni les remplacer.
    for colonne in ("lat", "long"):
        c[colonne] = (
            c[colonne]
            .astype("string")
            .str.strip()
            .str.replace(",", ".", regex=False)
        )

    resultat["caracteristiques"] = c

    return resultat
