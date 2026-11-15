"""WP2 - Typage BAAC et construction des dates/heures."""
import pandas as pd

ENTIERS = {
    "caracteristiques": [
        "jour", "mois", "an", "lum", "agg", "int", "atm", "col"
    ],
    "lieux": [
        "catr", "circ", "nbv", "vosp", "prof", "plan",
        "surf", "infra", "situ", "vma"
    ],
    "usagers": [
        "place", "catu", "grav", "sexe", "an_nais",
        "trajet", "secu1", "secu2", "secu3",
        "locp", "etatp"
    ],
    "vehicules": [
        "senc", "catv", "obs", "obsm", "choc",
        "manv", "motor", "occutc"
    ],
}

DECIMAUX = {
    "caracteristiques": ["lat", "long"],
    "lieux": ["lartpc", "larrout"],
}

def convertir(serie, type_cible, famille, colonne):
    valeurs = (
        serie.astype("string")
        .str.strip()
        .str.replace(",", ".", regex=False)
    )
    valeurs = valeurs.mask(
        valeurs.str.lower().isin(
            ["", "n/a", "null", "nan", "none", "#valeurmulti", "#erreur"]
        ).fillna(False)
    )

    nombres = pd.to_numeric(valeurs, errors="coerce")

    # Ne jamais masquer silencieusement une valeur mal formee.
    invalides = valeurs.notna() & nombres.isna()
    if invalides.any():
        raise ValueError(
            f"{famille}.{colonne}: "
            f"{int(invalides.sum())} valeurs non numeriques"
        )

    if type_cible == "Int64":
        fractionnaires = nombres.notna() & (nombres % 1 != 0)
        if fractionnaires.any():
            raise ValueError(
                f"{famille}.{colonne}: valeurs non entieres"
            )

    return nombres.astype(type_cible)


def appliquer(t: dict) -> dict:
    resultat = {}

    for famille, source in t.items():
        df = source.copy()

        for colonne in ENTIERS.get(famille, []):
            df[colonne] = convertir(
                df[colonne], "Int64", famille, colonne
            )

        for colonne in DECIMAUX.get(famille, []):
            df[colonne] = convertir(
                df[colonne], "Float64", famille, colonne
            )

        if famille == "caracteristiques":
            df["date_accident"] = pd.to_datetime(
                {
                    "year": df["an"],
                    "month": df["mois"],
                    "day": df["jour"],
                },
                errors="coerce",
            )

            heure = df["hrmn"].astype("string").str.strip()

            # Accepte HH:MM et HHMM.
            heure = heure.str.replace(
                r"^(\d{2})(\d{2})$",
                r"\1:\2",
                regex=True
            )

            df["heure_accident"] = heure

            df["datetime_accident"] = pd.to_datetime(
                df["date_accident"].dt.strftime("%Y-%m-%d")
                + " " + heure,
                format="%Y-%m-%d %H:%M",
                errors="coerce",
            )

            if df["datetime_accident"].isna().any():
                raise ValueError(
                    "Dates ou heures d'accident invalides : "
                    f"{int(df['datetime_accident'].isna().sum())}"
                )

        resultat[famille] = df

    return resultat
