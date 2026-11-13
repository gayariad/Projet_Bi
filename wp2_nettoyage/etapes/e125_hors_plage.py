"""WP2 - Signalement des valeurs hors plage sans suppression."""
import pandas as pd


def appliquer(t: dict) -> dict:
    resultat = dict(t)

    if "caracteristiques" in t:
        df = t["caracteristiques"].copy()
        lat = pd.to_numeric(df["lat"], errors="coerce")
        lon = pd.to_numeric(df["long"], errors="coerce")

        # Coordonnees BAAC en degres decimaux.
        df["coordonnees_suspectes"] = (
            ((lat == 0) & (lon == 0))
            | lat.notna() & ~lat.between(-90, 90)
            | lon.notna() & ~lon.between(-180, 180)
        ).fillna(False)

        resultat["caracteristiques"] = df

    if "lieux" in t:
        df = t["lieux"].copy()
        vma = pd.to_numeric(df["vma"], errors="coerce")

        # dans la réglementation la vma min est 20 mais peux être réduite par la maire a 10 dans certaines zones
        df["vma_suspecte"] = (
            (vma < 10) | (vma > 130)
        ).fillna(False)

        resultat["lieux"] = df

    return resultat
