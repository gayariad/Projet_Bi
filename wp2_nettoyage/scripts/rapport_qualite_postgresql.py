from pathlib import Path
import pandas as pd

from commun.recuperer_donnees import charger_tout
from wp2_nettoyage.pipeline import donnees_propres

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "cache" / "wp2_rapports"
MARQUEURS = {"", "n/a", "null", "nan", "none"}


def statistiques(tables, etape):
    lignes = []

    for famille, df in tables.items():
        for colonne in df.columns:
            valeurs = df[colonne].astype("string").str.strip()
            manquantes = (
                valeurs.isna()
                | valeurs.str.lower().isin(MARQUEURS).fillna(False)
            )

            lignes.append({
                "etape": etape,
                "famille": famille,
                "colonne": colonne,
                "lignes": len(df),
                "valeurs_manquantes": int(manquantes.sum()),
                "pourcentage_manquant": round(
                    100 * manquantes.mean(), 2
                ),
                "codes_moins_1": int(
                    valeurs.eq("-1").fillna(False).sum()
                ),
                "codes_zero": int(
                    valeurs.eq("0").fillna(False).sum()
                ),
            })

    return pd.DataFrame(lignes)


def main():
    brut = charger_tout()
    propre = donnees_propres()

    SORTIE.mkdir(parents=True, exist_ok=True)

    rapport = pd.concat(
        [
            statistiques(brut, "avant"),
            statistiques(propre, "apres"),
        ],
        ignore_index=True,
    )

    destination = SORTIE / "rapport_qualite_avant_apres.csv"
    rapport.to_csv(
        destination,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print("Rapport cree :", destination)
    print("Colonnes analysees :", sum(len(df.columns) for df in brut.values()))
    print("Lignes du rapport :", len(rapport))

    changements = (
        rapport.pivot(
            index=["famille", "colonne"],
            columns="etape",
            values="valeurs_manquantes",
        )
        .reset_index()
    )

    modifications = changements[
        changements["avant"] != changements["apres"]
    ]

    print("\n=== EVOLUTION DES VALEURS MANQUANTES ===")

    if modifications.empty:
        print("Aucune variation selon les marqueurs controles.")
    else:
        print(modifications.to_string(index=False))

    print("\nRappel : les regles de nettoyage sont actives dans propre_v1 candidate et restent a valider.")


if __name__ == "__main__":
    main()
