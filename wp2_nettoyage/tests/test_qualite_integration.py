"""Controles qualite et integrite du pipeline BAAC."""

import pytest

from wp2_nettoyage.pipeline import donnees_propres

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def tables():
    return donnees_propres()


def test_integrite_accidents(tables):
    c = tables["caracteristiques"]
    assert c["num_acc"].is_unique

    accidents = set(c["num_acc"].dropna())

    for nom in ("lieux", "vehicules", "usagers"):
        assert tables[nom]["num_acc"].isin(accidents).all()


def test_integrite_vehicules_usagers(tables):
    usagers = tables["usagers"]
    vehicules = tables["vehicules"]

    cles = set(
        zip(vehicules["num_acc"], vehicules["id_vehicule"])
    )

    for cle in zip(usagers["num_acc"], usagers["id_vehicule"]):
        assert cle in cles


def test_doublons_usagers_historiques(tables):
    usagers = tables["usagers"]

    doublons = usagers[usagers.duplicated()]

    assert len(doublons) == 164
    assert set(doublons["annee"].unique()).issubset({2019, 2020})

    # Les doublons sont conserves en attente de validation.
    assert len(usagers) == 745158
