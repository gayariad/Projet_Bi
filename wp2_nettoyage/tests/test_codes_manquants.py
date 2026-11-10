import pandas as pd

from wp2_nettoyage.etapes.e120_valeurs_manquantes import appliquer, charger_referentiel


def referentiel(lignes):
    ref = pd.DataFrame(lignes, columns=["famille", "variable", "code", "annee_min", "annee_max", "action"])
    ref["code"] = pd.to_numeric(ref["code"])
    return ref


def test_moins_un_et_zero_selon_la_variable():
    ref = referentiel([
        ["vehicules", "manv", -1, 2019, 2024, "NA"],
        ["vehicules", "manv", 0, 2019, 2024, "NA"],
        ["vehicules", "obs", 0, 2019, 2024, "CONSERVER"],
        ["vehicules", "obs", -1, 2019, 2024, "NA"],
    ])
    t = {"vehicules": pd.DataFrame({
        "num_acc": ["1", "2", "3"],
        "annee": [2020, 2020, 2020],
        "manv": pd.Series([-1, 0, 2], dtype="Int64"),
        "obs": pd.Series([-1, 0, 1], dtype="Int64"),
    })}

    v = appliquer(t, ref)["vehicules"]

    assert v["manv"].isna().tolist() == [True, True, False]
    assert v["obs"].isna().tolist() == [True, False, False]
    assert str(v["manv"].dtype) == "Int64"
    assert len(v) == 3


def test_regle_limitee_a_certaines_annees():
    ref = referentiel([["usagers", "trajet", 0, 2019, 2020, "NA"]])
    t = {"usagers": pd.DataFrame({
        "num_acc": ["1", "2"],
        "annee": [2019, 2023],
        "trajet": pd.Series([0, 0], dtype="Int64"),
    })}

    u = appliquer(t, ref)["usagers"]

    assert u["trajet"].isna().tolist() == [True, False]


def test_identifiants_jamais_modifies():
    ref = referentiel([["usagers", "grav", -1, 2019, 2024, "NA"]])
    t = {"usagers": pd.DataFrame({
        "num_acc": ["-1", ""],
        "annee": [2020, 2020],
        "grav": ["-1", "2"],
    })}

    u = appliquer(t, ref)["usagers"]

    assert u["num_acc"].tolist() == ["-1", ""]


def test_referentiel_officiel_valide():
    ref = charger_referentiel()

    assert set(ref["action"]) <= {"NA", "CONSERVER"}
    assert not ref.duplicated(["famille", "variable", "code", "annee_min"]).any()
    # Les zeros qui sont de vraies modalites restent conserves.
    conserves = ref[(ref["code"] == 0) & (ref["action"] == "CONSERVER")]
    assert {"infra", "vosp", "obs", "secu1"} <= set(conserves["variable"])
