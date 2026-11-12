import pandas as pd
import pytest
from wp2_nettoyage.etapes.e125_hors_plage import appliquer


def test_coordonnees_suspectes():
    """verifie les coordonnees GPS valides, point (0,0), hors limites et invalides."""
    df_caract = pd.DataFrame(
        {
            "lat": [48.8566, 0.0, 95.0, -91.0, 48.0, "invalide"],
            "long": [2.3522, 0.0, 2.35, 2.35, 185.0, "abc"],
        }
    )

    res = appliquer({"caracteristiques": df_caract})
    df_res = res["caracteristiques"]

    # (48.85, 2.35) -> Valide (False)
    # (0, 0) -> Suspect (True)
    # Lat 95 -> Hors plage (True)
    # Lat -91 -> Hors plage (True)
    # Long 185 -> Hors plage (True)
    # Texte non numerique -> Converti en NaN puis False
    attendu = [False, True, True, True, True, False]
    assert df_res["coordonnees_suspectes"].tolist() == attendu


def test_vma_suspecte():
    """verifie les vitesse hors intervalle [10, 130]."""
    df_lieux = pd.DataFrame(
        {"vma": [50, 130, 0, -10, 140, "texte_invalide"]}
    )

    res = appliquer({"lieux": df_lieux})
    df_res = res["lieux"]

    # 50 -> Valide (False)
    # 130 -> Valide (False)
    # 0 -> invalide (True)
    # -10 -> Negatif (True)
    # 140 -> Superieur à 130 (True)
    # Non numerique -> NaN (False)
    attendu = [False, False, True, True, True, False]
    assert df_res["vma_suspecte"].tolist() == attendu


def test_traitement_independant_des_tables():
    """verifie que tout fonctionne si il n'y a qu'une seule table"""
    df_caract = pd.DataFrame({"lat": [48.0], "long": [2.0]})
    res = appliquer({"caracteristiques": df_caract})

    assert "caracteristiques" in res
    assert "coordonnees_suspectes" in res["caracteristiques"].columns
    assert "lieux" not in res


def test_immutabilite():
    """verifie qu'il n'y a pas d'alteration dans les dataframe d'origine"""
    df_caract = pd.DataFrame({"lat": [48.0], "long": [2.0]})
    df_lieux = pd.DataFrame({"vma": [50]})
    entree = {"caracteristiques": df_caract, "lieux": df_lieux}

    appliquer(entree)

    assert "coordonnees_suspectes" not in df_caract.columns
    assert "vma_suspecte" not in df_lieux.columns