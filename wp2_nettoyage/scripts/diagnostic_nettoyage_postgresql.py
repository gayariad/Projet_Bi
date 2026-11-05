"""Diagnostic WP2 des valeurs speciales avant nettoyage.

Lecture seule. Ne modifie aucune donnee.
"""

from pathlib import Path
import pandas as pd

from commun.recuperer_donnees import charger_tout


def diagnostiquer(tables):
    lieux = tables["lieux"]

    for colonne in ("larrout", "v2"):
        print(f"\n=== VARIABLE : {colonne} ===")

        valeurs = lieux[colonne].astype("string").str.strip()

        resultat = (
            pd.DataFrame({
                "annee": lieux["annee"],
                "valeur": valeurs.fillna("<NULL_PANDAS>")
            })
            .groupby(["annee", "valeur"], dropna=False)
            .size()
            .reset_index(name="nombre")
        )

        for annee in sorted(resultat["annee"].unique()):
            sous_ensemble = resultat[
                resultat["annee"] == annee
            ].sort_values("nombre", ascending=False)

            print(f"\nANNEE {annee}")
            print(sous_ensemble.head(12).to_string(index=False))

        print("\nValeurs particulieres :")

        speciaux = valeurs.isna() | valeurs.str.lower().isin(
            ["", "-1", "n/a", "null", "nan", "none"]
        ).fillna(False)

        resume = (
            pd.DataFrame({
                "annee": lieux["annee"],
                "special": speciaux
            })
            .groupby("annee")["special"]
            .agg(["sum", "count"])
        )

        resume["pourcentage"] = (
            100 * resume["sum"] / resume["count"]
        ).round(2)

        print(resume.to_string())


if __name__ == "__main__":
    tables = charger_tout()
    diagnostiquer(tables)
