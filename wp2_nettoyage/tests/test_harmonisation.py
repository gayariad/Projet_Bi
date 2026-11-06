import pandas as pd

from wp2_nettoyage.etapes.e110_harmonisation import appliquer


def test_harmonisation_coordonnees():
    brut = {
        "caracteristiques": pd.DataFrame({
            "num_acc": ["1", "2", "3"],
            "annee": [2019, 2020, 2024],
            "lat": ["48,8566", " 49,1234 ", None],
            "long": ["2,3522", " 6,1234 ", None]
        }),
        "lieux": pd.DataFrame({
            "num_acc": ["1", "2", "3"],
            "annee": [2019, 2020, 2024]
        })
    }

    resultat = appliquer(brut)

    assert len(resultat["caracteristiques"]) == 3
    assert resultat["caracteristiques"]["lat"].iloc[0] == "48.8566"
    assert resultat["caracteristiques"]["long"].iloc[1] == "6.1234"
    assert pd.isna(resultat["caracteristiques"]["lat"].iloc[2])

    assert resultat["caracteristiques"]["num_acc"].tolist() == ["1", "2", "3"]
    assert resultat["lieux"].equals(brut["lieux"])

    # Le module ne doit pas modifier les données d'entrée.
    assert brut["caracteristiques"]["lat"].iloc[0] == "48,8566"

    # Vérification de l'idempotence.
    deuxieme = appliquer(resultat)
    pd.testing.assert_frame_equal(
        resultat["caracteristiques"],
        deuxieme["caracteristiques"]
    )
