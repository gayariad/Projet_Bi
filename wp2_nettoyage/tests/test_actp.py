import pandas as pd
from wp2_nettoyage.etapes.e120_valeurs_manquantes import appliquer


def test_actp_moins_un_texte():
    brut = {
        "usagers": pd.DataFrame({
            "actp": ["-1", "-1.0", "A", "B", "0"]
        })
    }

    resultat = appliquer(brut)["usagers"]["actp"]

    assert resultat.isna().sum() == 3
    assert resultat.iloc[2] == "A"
    assert pd.isna(resultat.iloc[3])
    assert resultat.iloc[4] == "0"
