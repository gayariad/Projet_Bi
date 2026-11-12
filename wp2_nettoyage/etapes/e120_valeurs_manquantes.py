"""WP2 - Nettoyage des valeurs manquantes BAAC (regles R003, R004 et codes -1/0).

1. Les marqueurs textuels d'absence (N/A, null, chaine vide...) deviennent pd.NA,
   sauf dans les identifiants.
2. Les variantes d'ecriture connues sont ramenees au code officiel :
   pr et pr1 valent "(1)" au lieu de -1 dans les millesimes 2019-2022.
3. Les codes -1 et 0 sont traites variable par variable selon le referentiel
   metadata/nettoyage/codes_manquants.csv (valide par Febbe avec la notice
   ONISR d'octobre 2025) :
   - action NA        : le code signifie "non renseigne" ou "inconnu" -> pd.NA
   - action CONSERVER : le code est une vraie modalite ("aucun", "sans objet")
   Seules les regles dont le statut commence par "valide" sont appliquees.
   Les regles "a_valider" ou "a_confirmer" restent en attente.

Annee de chaque ligne (pour annee_min / annee_max) :
   - colonne "annee" si elle existe, sinon colonne "an" ;
   - sinon, l'annee est recuperee depuis caracteristiques.an via num_acc.
   Une regle limitee a certaines annees n'est jamais appliquee a une ligne
   dont l'annee est inconnue. Une regle couvrant toute la periode 2019-2024
   s'applique sans condition d'annee.

Aucune ligne n'est supprimee. L'etape est idempotente.
"""
from pathlib import Path

import pandas as pd

MARQUEURS = {"", "n/a", "null", "nan", "none"}

IDENTIFIANTS = {"num_acc", "id_vehicule", "id_usager", "num_veh", "dep", "com"}

VARIANTES = {
    "pr": {"(1)": "-1"},
    "pr1": {"(1)": "-1"},
}

PERIODE_MIN, PERIODE_MAX = 2019, 2024

REFERENTIEL = (
    Path(__file__).resolve().parents[1]
    / "metadata" / "nettoyage" / "codes_manquants.csv"
)


def charger_referentiel(chemin=REFERENTIEL) -> pd.DataFrame:
    ref = pd.read_csv(
        chemin, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False
    )
    attendues = {
        "famille", "variable", "code", "annee_min", "annee_max", "action", "statut"
    }
    manquantes = attendues - set(ref.columns)
    if manquantes:
        raise ValueError(f"Referentiel incomplet, colonnes absentes : {manquantes}")

    ref["action"] = ref["action"].str.strip().str.upper()
    actions = set(ref["action"])
    if not actions <= {"NA", "CONSERVER"}:
        raise ValueError(f"Actions inconnues dans le referentiel : {actions}")

    ref["statut"] = ref["statut"].str.strip().str.lower()
    ref["code"] = pd.to_numeric(ref["code"])
    ref["annee_min"] = pd.to_numeric(ref["annee_min"])
    ref["annee_max"] = pd.to_numeric(ref["annee_max"])
    return ref


def regles_applicables(ref: pd.DataFrame) -> pd.DataFrame:
    """Regles validees qui transforment un code en NA."""
    valide = ref["statut"].str.startswith("valid")
    return ref[valide & (ref["action"] == "NA")]


def annees_par_accident(t: dict):
    """Serie num_acc -> annee, construite depuis caracteristiques."""
    car = t.get("caracteristiques")
    if car is None or "num_acc" not in car.columns:
        return None
    colonne = "an" if "an" in car.columns else "annee" if "annee" in car.columns else None
    if colonne is None:
        return None
    annees = pd.Series(
        pd.to_numeric(car[colonne].astype("string"), errors="coerce").to_numpy(),
        index=car["num_acc"].astype("string").to_numpy(),
    )
    return annees[~annees.index.duplicated()]


def annee_des_lignes(df: pd.DataFrame, annees_acc) -> pd.Series:
    for colonne in ("annee", "an"):
        if colonne in df.columns:
            return pd.to_numeric(df[colonne].astype("string"), errors="coerce")
    if annees_acc is not None and "num_acc" in df.columns:
        cles = df["num_acc"].astype("string")
        return pd.Series(cles.map(annees_acc).to_numpy(), index=df.index, dtype="Float64")
    return pd.Series(pd.NA, index=df.index, dtype="Float64")


def normaliser_marqueurs(df: pd.DataFrame) -> pd.DataFrame:
    for colonne in df.select_dtypes(include=["object", "string"]).columns:
        if colonne in IDENTIFIANTS:
            continue
        valeurs = df[colonne].astype("string").str.strip()
        masque = valeurs.str.lower().isin(MARQUEURS).fillna(False)
        df[colonne] = valeurs.mask(masque, pd.NA)
    return df


def normaliser_variantes(df: pd.DataFrame) -> pd.DataFrame:
    for colonne, correspondances in VARIANTES.items():
        if colonne in df.columns:
            valeurs = df[colonne].astype("string").str.strip()
            df[colonne] = valeurs.replace(correspondances)
    return df


def appliquer_codes(df, famille, regles, annee) -> pd.DataFrame:
    for regle in regles[regles["famille"] == famille].itertuples():
        if regle.variable not in df.columns:
            continue

        valeurs = pd.to_numeric(df[regle.variable].astype("string"), errors="coerce")
        masque = (valeurs == regle.code).fillna(False)

        toute_la_periode = (
            regle.annee_min <= PERIODE_MIN and regle.annee_max >= PERIODE_MAX
        )
        if not toute_la_periode:
            dans_periode = annee.between(regle.annee_min, regle.annee_max)
            masque &= dans_periode.fillna(False).astype(bool)

        df[regle.variable] = df[regle.variable].mask(masque, pd.NA)

    return df


def appliquer(t: dict, referentiel: pd.DataFrame = None) -> dict:
    ref = charger_referentiel() if referentiel is None else referentiel
    if "statut" not in ref.columns:
        ref = ref.assign(statut="valide")
    regles = regles_applicables(ref)
    annees_acc = annees_par_accident(t)

    resultat = {}
    for famille, source in t.items():
        df = source.copy()
        df = normaliser_marqueurs(df)
        df = normaliser_variantes(df)
        annee = annee_des_lignes(df, annees_acc)
        df = appliquer_codes(df, famille, regles, annee)
        resultat[famille] = df

    return resultat
