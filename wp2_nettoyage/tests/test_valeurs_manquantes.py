import pandas as pd

from wp2_nettoyage.etapes.e120_valeurs_manquantes import appliquer


def test_normalisation_v2():
    brut = {
        "lieux": pd.DataFrame({
            "num_acc": ["1", "2", "3", "4", "5", "6"],
            "annee": [2020, 2021, 2022, 2023, 2024, 2024],
            "v2": ["N/A", "null", None, "A", "D", "-"]
        })
    }

    resultat = appliquer(brut)

    assert resultat["lieux"]["v2"].isna().sum() == 3
    assert resultat["lieux"]["v2"].iloc[3:].tolist() == ["A", "D", "-"]
    assert len(resultat["lieux"]) == 6

    # Les données d'entrée ne sont pas modifiées.
    assert brut["lieux"]["v2"].iloc[0] == "N/A"

    # L'application répétée ne change pas le résultat.
    deuxieme = appliquer(resultat)
    pd.testing.assert_frame_equal(
        resultat["lieux"],
        deuxieme["lieux"]
    )
