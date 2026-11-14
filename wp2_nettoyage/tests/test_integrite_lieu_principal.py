"""Controle d'integrite du lieu principal sur les donnees BAAC reelles."""

import pandas as pd
from commun.recuperer_donnees import charger_tout
from wp2_nettoyage.pipeline import donnees_propres


def test_integrite_lieu_principal():
    brutes = charger_tout()["lieux"]
    propres = donnees_propres()["lieux"]

    assert len(propres) == len(brutes) == 359512

    assert "lieu_principal" in propres.columns

    principaux = propres["lieu_principal"]
    assert principaux.notna().all()
    assert pd.api.types.is_bool_dtype(principaux.dtype)

    nombre_par_accident = (
        propres.groupby("num_acc")["lieu_principal"].sum()
    )
    assert nombre_par_accident.eq(1).all()
