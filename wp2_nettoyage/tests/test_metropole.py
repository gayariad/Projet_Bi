import pandas as pd
import pytest
from wp2_nettoyage.etapes.e130_metropole import DEPARTEMENTS_METROPOLE, appliquer


@pytest.fixture
def base_dict():
    """Fixture avec plusieurs cas de departements"""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7],
            "dep": [
                "75",
                "2A",
                "2B",
                "971",
                "01",
                " 13 ",
                "20",
            ],
        }
    )
    return {"caracteristiques": df, "autre_cle": "valeur"}


def test_identification_metropole(base_dict):
    """verifie la bonne dispertion des departements"""
    res = appliquer(base_dict)
    df_res = res["caracteristiques"]

    # 75, 2A, 2B, 01, 13 sont en métropole
    # 971 et 20 ne le sont pas
    attendu = [True, True, True, False, True, True, False]
    assert df_res["metropole"].tolist() == attendu


def test_sans_cle_caracteristiques():
    """verifie que la fonction renvoie un dictionnaire inchange si la cle est absente"""
    entree = {"autre_donnees": [1, 2, 3]}
    res = appliquer(entree)

    assert res == entree
    assert res is not entree  # s'assure qu'une nouvelle copie du dictionnaire est créée


def test_immutabilite_dataframe_original(base_dict):
    """verifie que le DataFrame d'origine dans le dictionnaire n'est pas modifié"""
    df_original = base_dict["caracteristiques"].copy()
    appliquer(base_dict)

    # la colonne metropole ne doit pas etre ajoutee a l'original
    assert "metropole" not in base_dict["caracteristiques"].columns
    pd.testing.assert_frame_equal(base_dict["caracteristiques"], df_original)


def test_formatage_chaine():
    """verifie la prise en compte des espaces et des minuscules."""
    df = pd.DataFrame({"dep": [" 2a ", "  75", "974  "]})
    res = appliquer({"caracteristiques": df})

    assert res["caracteristiques"]["metropole"].tolist() == [True, True, False]