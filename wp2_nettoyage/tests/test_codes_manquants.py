import pandas as pd

from wp2_nettoyage.etapes.e120_valeurs_manquantes import (
    appliquer,
    charger_referentiel,
    regles_applicables,
)


def referentiel(lignes):
    ref = pd.DataFrame(
        lignes,
        columns=["famille", "variable", "code", "annee_min", "annee_max", "action", "statut"],
    )
    ref["code"] = pd.to_numeric(ref["code"])
    return ref


def test_moins_un_et_zero_selon_la_variable():
    ref = referentiel([
        ["vehicules", "manv", -1, 2019, 2024, "NA", "valide"],
        ["vehicules", "manv", 0, 2019, 2024, "NA", "valide"],
        ["vehicules", "obs", 0, 2019, 2024, "CONSERVER", "valide"],
        ["vehicules", "obs", -1, 2019, 2024, "NA", "valide"],
    ])
    t = {"vehicules": pd.DataFrame({
        "num_acc": ["1", "2", "3"],
        "manv": pd.Series([-1, 0, 2], dtype="Int64"),
        "obs": pd.Series([-1, 0, 1], dtype="Int64"),
    })}

    v = appliquer(t, ref)["vehicules"]

    assert v["manv"].isna().tolist() == [True, True, False]
    assert v["obs"].isna().tolist() == [True, False, False]
    assert str(v["manv"].dtype) == "Int64"
    assert len(v) == 3


def test_regle_non_validee_jamais_appliquee():
    ref = referentiel([
        ["lieux", "v1", -1, 2019, 2024, "NA", "a_valider"],
        ["lieux", "nbv", 0, 2019, 2024, "NA", "a_confirmer_onisr"],
        ["lieux", "nbv", -1, 2019, 2024, "NA", "valide"],
    ])
    t = {"lieux": pd.DataFrame({
        "num_acc": ["1", "2"],
        "v1": pd.Series([-1, 2], dtype="Int64"),
        "nbv": pd.Series([0, -1], dtype="Int64"),
    })}

    lieux = appliquer(t, ref)["lieux"]

    assert lieux["v1"].tolist()[0] == -1
    assert lieux["nbv"].tolist()[0] == 0
    assert pd.isna(lieux["nbv"].iloc[1])


def test_annee_recuperee_depuis_caracteristiques():
    ref = referentiel([["usagers", "trajet", 0, 2019, 2020, "NA", "valide"]])
    t = {
        "caracteristiques": pd.DataFrame({
            "num_acc": ["201900000001", "202300000002"],
            "an": pd.Series([2019, 2023], dtype="Int64"),
        }),
        "usagers": pd.DataFrame({
            "num_acc": ["201900000001", "202300000002", "202300000002"],
            "trajet": pd.Series([0, 0, 1], dtype="Int64"),
        }),
    }

    u = appliquer(t, ref)["usagers"]

    assert u["trajet"].isna().tolist() == [True, False, False]


def test_regle_limitee_ignoree_si_annee_inconnue():
    ref = referentiel([
        ["lieux", "v1", -1, 2020, 2024, "NA", "valide"],
        ["lieux", "circ", -1, 2019, 2024, "NA", "valide"],
    ])
    t = {"lieux": pd.DataFrame({
        "num_acc": ["1"],
        "v1": pd.Series([-1], dtype="Int64"),
        "circ": pd.Series([-1], dtype="Int64"),
    })}

    lieux = appliquer(t, ref)["lieux"]

    # Annee inconnue : la regle 2020-2024 n'est pas appliquee...
    assert lieux["v1"].iloc[0] == -1
    # ... mais la regle valable sur toute la periode l'est.
    assert pd.isna(lieux["circ"].iloc[0])


def test_pr_ecrit_entre_parentheses():
    ref = referentiel([
        ["lieux", "pr", -1, 2019, 2024, "NA", "valide"],
        ["lieux", "pr1", -1, 2019, 2024, "NA", "valide"],
    ])
    t = {"lieux": pd.DataFrame({
        "num_acc": ["1", "2", "3"],
        "pr": ["(1)", "-1", "12"],
        "pr1": ["(1)", "350", "-1"],
    })}

    lieux = appliquer(t, ref)["lieux"]

    assert lieux["pr"].isna().tolist() == [True, True, False]
    assert lieux["pr1"].isna().tolist() == [True, False, True]

    # Idempotence.
    pd.testing.assert_frame_equal(lieux, appliquer({"lieux": lieux}, ref)["lieux"])


def test_identifiants_jamais_modifies():
    ref = referentiel([["usagers", "grav", -1, 2019, 2024, "NA", "valide"]])
    t = {"usagers": pd.DataFrame({
        "num_acc": ["-1", ""],
        "grav": ["-1", "2"],
    })}

    u = appliquer(t, ref)["usagers"]

    assert u["num_acc"].tolist() == ["-1", ""]


def test_referentiel_officiel_valide():
    ref = charger_referentiel()
    applicables = regles_applicables(ref)

    assert set(ref["action"]) <= {"NA", "CONSERVER"}
    assert {"type_valeur", "source", "remarque"} <= set(ref.columns)
    assert not ref.duplicated(["famille", "variable", "code", "annee_min"]).any()

    # Codes 0 valides par Febbe avec la notice ONISR.
    zeros_na = applicables[applicables["code"] == 0]
    assert {"trajet", "senc", "manv", "motor", "catv"} <= set(zeros_na["variable"])

    # Regles encore a valider : jamais appliquees.
    en_attente = ref[~ref["statut"].str.startswith("valid")]
    assert {"v1", "nbv"} <= set(en_attente["variable"])
    assert applicables.merge(en_attente, how="inner").empty

    # Les zeros qui sont de vraies modalites restent conserves.
    conserves = ref[(ref["code"] == 0) & (ref["action"] == "CONSERVER")]
    assert {"infra", "vosp", "obs", "secu1", "actp"} <= set(conserves["variable"])
