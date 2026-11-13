import pandas as pd
import pytest
from wp2_nettoyage.etapes.e140_doublons import appliquer


def test_identification_doublons():
    """verifie que toutes les occurrences d'un doublon sont marquees a True"""
    df = pd.DataFrame(
        {
            "id": [101, 102, 102, 103],
            "nom": ["Martin", "Dupont", "Dupont", "Durand"],
        }
    )

    res = appliquer({"usagers": df})
    assert res["usagers"]["doublon_suspect"].tolist() == [
        False,
        True,
        True,
        False,
    ]


def test_aucun_doublon():
    """verifie que toutes les lignes renvoient False s'il n'y a pas de doublon"""
    df = pd.DataFrame(
        {"id": [101, 102, 103], "nom": ["Martin", "Dupont", "Durand"]}
    )

    res = appliquer({"usagers": df})
    assert res["usagers"]["doublon_suspect"].tolist() == [False, False, False]


def test_toutes_lignes_identiques():
    """verifie que toutes les lignes renvoient True si toutes sont en double"""
    df = pd.DataFrame({"id": [101, 101], "nom": ["Martin", "Martin"]})

    res = appliquer({"usagers": df})
    assert res["usagers"]["doublon_suspect"].tolist() == [True, True]


def test_sans_cle_usagers():
    """verifie que le dictionnaire est renvoye intact si la cle usagers est absente"""
    entree = {"autre_table": pd.DataFrame({"a": [1]})}
    res = appliquer(entree)

    assert res == entree
    assert res is not entree


def test_immutabilite_dataframe_original():
    """verifie que le DataFrame d'origine n'est pas modifie"""
    df_original = pd.DataFrame({"id": [101, 101], "nom": ["Martin", "Martin"]})
    entree = {"usagers": df_original}

    appliquer(entree)

    assert "doublon_suspect" not in df_original.columns