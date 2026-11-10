import pandas as pd
import pytest

from wp2_nettoyage.etapes.e115_typage import appliquer as typer
from wp2_nettoyage.etapes.e120_valeurs_manquantes import appliquer as nettoyer
from wp2_nettoyage.pipeline import donnees_propres


def test_typage_et_date():
    brut = {
        "caracteristiques": pd.DataFrame({
            "num_acc": ["1"],
            "jour": ["09"],
            "mois": ["11"],
            "an": ["2026"],
            "lum": ["1"],
            "agg": ["2"],
            "int": ["1"],
            "atm": ["1"],
            "col": ["3"],
            "lat": ["48,8566"],
            "long": ["2,3522"],
            "hrmn": ["14:30"],
        })
    }

    resultat = typer(brut)["caracteristiques"]

    assert str(resultat["lat"].dtype) == "Float64"
    assert str(resultat["jour"].dtype) == "Int64"
    assert resultat["date_accident"].iloc[0] == pd.Timestamp("2026-11-09")
    assert resultat["heure_accident"].iloc[0] == "14:30"
    assert resultat["datetime_accident"].iloc[0] == pd.Timestamp("2026-11-09 14:30")


def test_nettoyage_codes():
    brut = {
        "lieux": pd.DataFrame({
            "num_acc": ["1", "2", "3"],
            "larrout": pd.Series([-1.0, 5.5, 0.0], dtype="Float64"),
            "v2": ["N/A", "A", "null"],
        })
    }

    resultat = nettoyer(brut)["lieux"]

    assert pd.isna(resultat["larrout"].iloc[0])
    assert resultat["larrout"].iloc[1] == 5.5
    assert resultat["larrout"].iloc[2] == 0
    assert pd.isna(resultat["v2"].iloc[0])
    assert resultat["v2"].iloc[1] == "A"
    assert pd.isna(resultat["v2"].iloc[2])


def test_pipeline_v1_reel():
    t = donnees_propres()

    assert len(t["caracteristiques"]) == 327628
    assert len(t["lieux"]) == 359512
    assert len(t["usagers"]) == 745158
    assert len(t["vehicules"]) == 559847

    c = t["caracteristiques"]
    assert str(c["lat"].dtype) == "Float64"
    assert c["datetime_accident"].notna().all()

    assert int(t["lieux"]["v2"].isna().sum()) == 330436
    assert int(t["usagers"].duplicated().sum()) == 164
