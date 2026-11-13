"""WP2 - Identification des accidents en France metropolitaine."""

DEPARTEMENTS_METROPOLE = {
    f"{i:02d}" for i in range(1, 96)
} - {"20"} | {"2A", "2B"}


def appliquer(t: dict) -> dict:
    resultat = dict(t)

    if "caracteristiques" in t:
        df = t["caracteristiques"].copy()
        dep = df["dep"].astype("string").str.strip().str.upper()

        df["metropole"] = dep.isin(DEPARTEMENTS_METROPOLE)
        resultat["caracteristiques"] = df

    return resultat
