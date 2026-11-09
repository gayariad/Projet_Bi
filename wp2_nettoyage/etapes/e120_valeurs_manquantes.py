"""WP2 - Nettoyage des valeurs manquantes BAAC.

Regles candidates pour propre_v1.
Les modalites doivent etre validees avec la notice ONISR.
"""
import pandas as pd

MARQUEURS = {"", "n/a", "null", "nan", "none"}

# Codes -1 proposes comme non renseignes.
# A confirmer variable par variable avant livraison definitive.
MOINS_UN_NA = {
    "caracteristiques": [
        "lum", "int", "atm", "col"
    ],
    "lieux": [
        "circ", "nbv", "vosp", "prof", "plan",
        "surf", "infra", "situ", "vma", "larrout"
    ],
    "usagers": [
        "place", "grav", "sexe", "trajet",
        "secu1", "secu2", "secu3",
        "locp", "actp", "etatp"
    ],
    "vehicules": [
        "senc", "catv", "obs", "obsm",
        "choc", "manv", "motor"
    ],
}


def appliquer(t: dict) -> dict:
    resultat = {}

    for famille, source in t.items():
        df = source.copy()

        # Normaliser les marqueurs textuels, sans modifier les IDs.
        identifiants = {
            "num_acc", "id_vehicule", "id_usager",
            "num_veh", "dep", "com"
        }

        for colonne in df.select_dtypes(
            include=["object", "string"]
        ).columns:
            if colonne in identifiants:
                continue

            valeurs = df[colonne].astype("string").str.strip()
            masque = valeurs.str.lower().isin(MARQUEURS).fillna(False)
            df[colonne] = valeurs.mask(masque, pd.NA)

        # Normalisation ciblee des -1.
        for colonne in MOINS_UN_NA.get(famille, []):
            if colonne in df.columns:
                df[colonne] = df[colonne].mask(
                    df[colonne].eq(-1).fillna(False),
                    pd.NA
                )

        resultat[famille] = df

    return resultat
