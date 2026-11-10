"""WP2 - Nettoyage des valeurs manquantes BAAC (regles R003, R004 et codes -1/0).

1. Les marqueurs textuels d'absence (N/A, null, chaine vide...) deviennent pd.NA,
   sauf dans les identifiants.
2. Les codes -1 et 0 sont traites variable par variable selon le referentiel
   metadata/nettoyage/codes_manquants.csv :
   - action NA        : le code signifie "non renseigne" ou "inconnu" -> pd.NA
   - action CONSERVER : le code est une vraie modalite ("aucun", "sans objet") -> garde
   Chaque regle porte une periode (annee_min, annee_max) : si le sens d'un code
   change selon le millesime, il suffit d'ajouter une ligne par periode.

Le referentiel est maintenu avec Febbe (codifications ONISR).
Aucune ligne n'est supprimee. L'etape est idempotente.
"""
from pathlib import Path

import pandas as pd

MARQUEURS = {"", "n/a", "null", "nan", "none"}

IDENTIFIANTS = {"num_acc", "id_vehicule", "id_usager", "num_veh", "dep", "com"}

REFERENTIEL = (
    Path(__file__).resolve().parents[1]
    / "metadata" / "nettoyage" / "codes_manquants.csv"
)


def charger_referentiel(chemin=REFERENTIEL) -> pd.DataFrame:
    ref = pd.read_csv(chemin, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    attendues = {"famille", "variable", "code", "annee_min", "annee_max", "action"}
    manquantes = attendues - set(ref.columns)
    if manquantes:
        raise ValueError(f"Referentiel incomplet, colonnes absentes : {manquantes}")
    actions = set(ref["action"].str.upper())
    if not actions <= {"NA", "CONSERVER"}:
        raise ValueError(f"Actions inconnues dans le referentiel : {actions}")
    ref["action"] = ref["action"].str.upper()
    ref["code"] = pd.to_numeric(ref["code"])
    ref["annee_min"] = pd.to_numeric(ref["annee_min"])
    ref["annee_max"] = pd.to_numeric(ref["annee_max"])
    return ref


def normaliser_marqueurs(df: pd.DataFrame) -> pd.DataFrame:
    for colonne in df.select_dtypes(include=["object", "string"]).columns:
        if colonne in IDENTIFIANTS:
            continue
        valeurs = df[colonne].astype("string").str.strip()
        masque = valeurs.str.lower().isin(MARQUEURS).fillna(False)
        df[colonne] = valeurs.mask(masque, pd.NA)
    return df


def appliquer_codes(df: pd.DataFrame, famille: str, ref: pd.DataFrame) -> pd.DataFrame:
    regles = ref[(ref["famille"] == famille) & (ref["action"] == "NA")]

    for regle in regles.itertuples():
        if regle.variable not in df.columns:
            continue

        # Comparaison numerique : fonctionne pour Int64, Float64 et texte ("-1", "-1.0").
        valeurs = pd.to_numeric(df[regle.variable].astype("string"), errors="coerce")
        masque = (valeurs == regle.code).fillna(False)

        if "annee" in df.columns:
            annee = pd.to_numeric(df["annee"], errors="coerce")
            masque &= annee.between(regle.annee_min, regle.annee_max).fillna(False)

        df[regle.variable] = df[regle.variable].mask(masque, pd.NA)

    return df


def appliquer(t: dict, referentiel: pd.DataFrame = None) -> dict:
    ref = charger_referentiel() if referentiel is None else referentiel
    resultat = {}

    for famille, source in t.items():
        df = source.copy()
        df = normaliser_marqueurs(df)
        df = appliquer_codes(df, famille, ref)
        resultat[famille] = df

    return resultat
