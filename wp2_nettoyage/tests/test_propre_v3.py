"""Tests permanents des corrections propre_v3 validees par Baptiste."""

import pandas as pd

from wp2_nettoyage.etapes.e130_metropole import appliquer as e130
from wp2_nettoyage.etapes.e140_doublons import appliquer as e140
from wp2_nettoyage.etapes.e125_hors_plage import appliquer as e125
from wp2_nettoyage.etapes.e120_valeurs_manquantes import (
    appliquer as e120,
    corriger_annees_naissance,
)


def test_v3_departements():
    donnees = {
        "caracteristiques": pd.DataFrame({
            "dep": pd.Series(
                ["6", "06", "1", "2A", "2B", "971", "974"],
                dtype="string"
            )
        })
    }

    resultat = e130(donnees)["caracteristiques"]

    assert resultat["dep"].tolist() == [
        "06", "06", "01", "2A", "2B", "971", "974"
    ]

    assert resultat["metropole"].tolist() == [
        True, True, True, True, True, False, False
    ]

    assert str(resultat["dep"].dtype) == "string"
    assert len(resultat) == 7


def test_v3_doublons_sans_id_usager():
    donnees = {
        "usagers": pd.DataFrame({
            "num_acc": ["A1", "A1", "A2"],
            "id_usager": ["U1", "U2", "U3"],
            "grav": [1, 1, 2],
            "sexe": [1, 1, 2],
        })
    }

    resultat = e140(donnees)["usagers"]

    assert resultat["doublon_suspect"].tolist() == [
        True, True, False
    ]
    assert len(resultat) == 3

    # Une seconde execution doit conserver les memes resultats.
    resultat2 = e140({"usagers": resultat})["usagers"]

    assert resultat2["doublon_suspect"].equals(
        resultat["doublon_suspect"]
    )


def test_v3_vma_corrigee_et_signalee():
    donnees = {
        "lieux": pd.DataFrame({
            "vma": pd.Series(
                [300, 500, 700, 900, 90, 140],
                dtype="Int64"
            )
        })
    }

    resultat = e125(donnees)["lieux"]

    assert resultat["vma"].tolist() == [
        30, 50, 70, 90, 90, 140
    ]

    assert resultat["vma_suspecte"].tolist() == [
        True, True, True, True, False, True
    ]

    assert str(resultat["vma"].dtype) == "Int64"

    resultat2 = e125({"lieux": resultat})["lieux"]

    assert resultat2["vma"].equals(resultat["vma"])
    assert resultat2["vma_suspecte"].equals(
        resultat["vma_suspecte"]
    )


def test_v3_v1_et_nbv_na():
    donnees = {
        "lieux": pd.DataFrame({
            "v1": pd.Series(
                ["-1", "2"], dtype="string"
            ),
            "nbv": pd.Series(
                [0, 2], dtype="Int64"
            )
        })
    }

    resultat = e120(donnees)["lieux"]

    assert pd.isna(resultat["v1"].iloc[0])
    assert pd.isna(resultat["nbv"].iloc[0])

    assert resultat["v1"].iloc[1] == "2"
    assert resultat["nbv"].iloc[1] == 2

    assert str(resultat["v1"].dtype) == "string"
    assert str(resultat["nbv"].dtype) == "Int64"


def test_v3_actp_b_na():
    donnees = {
        "usagers": pd.DataFrame({
            "actp": pd.Series(
                ["B", "A", "7", "8", "0"],
                dtype="string"
            )
        })
    }

    resultat = e120(donnees)["usagers"]

    assert pd.isna(resultat["actp"].iloc[0])

    assert resultat["actp"].iloc[1:].tolist() == [
        "A", "7", "8", "0"
    ]

    assert str(resultat["actp"].dtype) == "string"


def test_v3_annees_naissance():
    # Accidents en 2020 :
    # 1900 -> NA
    # 1910 -> age 110 -> NA
    # 2025 -> age negatif -> NA
    # 1990 -> age 30 -> conserve
    # 1915 -> age 105 -> conserve
    donnees = pd.DataFrame({
        "an_nais": pd.Series(
            [1900, 1910, 2025, 1990, 1915],
            dtype="Int64"
        )
    })

    annees_accident = pd.Series(
        [2020, 2020, 2020, 2020, 2020]
    )

    resultat = corriger_annees_naissance(
        donnees, annees_accident
    )

    assert resultat["an_nais"].isna().tolist() == [
        True, True, True, False, False
    ]

    assert resultat["an_nais"].iloc[3] == 1990
    assert resultat["an_nais"].iloc[4] == 1915

    assert str(resultat["an_nais"].dtype) == "Int64"
    assert len(resultat) == 5
