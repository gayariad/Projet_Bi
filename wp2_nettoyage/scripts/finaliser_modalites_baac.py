"""Consolide le référentiel des modalités BAAC sans écraser les arbitrages WP2.

Usage (depuis racine du projet):
    python wp2_nettoyage/scripts/finaliser_modalites_baac.py

Idempotent : une seconde exécution ne change pas le fichier validé.
Le fichier final doit déjà exister et être alimenté par Lucas/Febbe.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CODIF = ROOT / "metadata" / "codifications"
MODALITES = CODIF / "modalites_baac_finalisees.csv"
REGLES = ROOT / "metadata" / "nettoyage" / "codes_manquants.csv"
RESERVES = CODIF / "codifications_a_confirmer.csv"

modalites = pd.read_csv(MODALITES, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
regles = pd.read_csv(REGLES, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
required = {"famille", "variable", "code", "libelle", "statut", "source", "annees", "remarque"}
if required - set(modalites.columns):
    raise ValueError(f"Colonnes manquantes dans modalites : {sorted(required - set(modalites.columns))}")
if modalites.duplicated(["famille", "variable", "code"]).any():
    raise ValueError("Doublons famille/variable/code dans le fichier des modalités")

# Alignement sur les seules décisions métiers validées dans codes_manquants.csv.
# Toute incohérence fait échouer la vérification : ne jamais remplacer silencieusement.
valides = regles[regles["statut"].str.lower().str.startswith("valide")]
for row in valides.itertuples(index=False):
    mask = (modalites["famille"] == row.famille) & (modalites["variable"] == row.variable) & (modalites["code"] == row.code)
    if not mask.any():
        # Le fichier des modalités peut être partiel pour certaines valeurs spéciales.
        continue
    if row.statut.lower() == "valide_reunion":
        states = set(modalites.loc[mask, "statut"].str.upper())
        if states != {"VALIDE_REUNION"}:
            raise ValueError(f"Décision réunion non reflétée : {row.famille}.{row.variable}={row.code}: {states}")

# Précision particulière : les décisions réunion existantes doivent rester intactes.
for famille, variable in [("caracteristiques", "int"), ("caracteristiques", "lum"),
                         ("usagers", "place"), ("usagers", "grav"),
                         ("usagers", "sexe"), ("vehicules", "catv")]:
    mask = (modalites["famille"] == famille) & (modalites["variable"] == variable) & (modalites["code"] == "-1")
    if not mask.any() or not (modalites.loc[mask, "statut"] == "VALIDE_REUNION").all():
        raise ValueError(f"Validation de réunion absente : {famille}.{variable}=-1")

reserves = regles[~regles["statut"].str.lower().str.startswith("valide")].copy()
reserves.to_csv(RESERVES, sep=";", index=False, encoding="utf-8-sig")
print(f"Modalités vérifiées : {len(modalites)} ; réserves : {len(reserves)}")
print("Décisions de réunion préservées ; aucune réécriture du fichier modalites_baac_finalisees.csv")
