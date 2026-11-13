import pandas as pd

from wp2_nettoyage.etapes.e150_lieu_principal import appliquer


def tables(lieux):
    return {"lieux": pd.DataFrame(lieux)}


def test_un_seul_lieu_principal_par_accident():
    t = tables({
        "num_acc": ["A", "A", "A", "B", "C", "C"],
        "catr": [3, 4, 3, 1, 2, 2],
        "voie": ["12", pd.NA, "12", "A6", pd.NA, "D7"],
        "vma": [50, pd.NA, 50, 130, 80, 80],
    })

    lieux = appliquer(t)["lieux"]

    assert len(lieux) == 6
    assert lieux.groupby("num_acc")["lieu_principal"].sum().eq(1).all()


def test_ligne_la_plus_complete_choisie():
    t = tables({
        "num_acc": ["A", "A"],
        "catr": [4, 4],
        "voie": [pd.NA, "D12"],
        "vma": [pd.NA, 50],
    })

    lieux = appliquer(t)["lieux"]

    assert lieux["lieu_principal"].tolist() == [False, True]


def test_egalite_departagee_par_categorie_de_route():
    t = tables({
        "num_acc": ["A", "A"],
        "catr": [3, 1],
        "voie": ["D12", "A6"],
    })

    lieux = appliquer(t)["lieux"]

    assert lieux["lieu_principal"].tolist() == [False, True]


def test_resultat_independant_de_l_ordre_des_lignes():
    t = tables({
        "num_acc": ["A", "A", "A", "B", "B"],
        "catr": [3, 3, 4, 2, 2],
        "voie": ["X", "Y", "Z", "N1", "N2"],
        "vma": [50, 50, 50, 90, 90],
    })
    melange = {"lieux": t["lieux"].iloc[[4, 2, 0, 3, 1]]}

    choix = appliquer(t)["lieux"]
    choix_melange = appliquer(melange)["lieux"]

    principaux = choix.loc[choix["lieu_principal"], "voie"].sort_values().tolist()
    principaux_melange = choix_melange.loc[choix_melange["lieu_principal"], "voie"].sort_values().tolist()
    assert principaux == principaux_melange


def test_aucune_ligne_supprimee_entree_intacte_et_idempotence():
    t = tables({
        "num_acc": ["A", "A", "B"],
        "catr": [3, 3, 1],
        "voie": ["D1", "D2", "A6"],
    })

    resultat = appliquer(t)
    deuxieme = appliquer(resultat)

    assert len(resultat["lieux"]) == 3
    assert "lieu_principal" not in t["lieux"].columns
    pd.testing.assert_frame_equal(resultat["lieux"], deuxieme["lieux"])
