"""Verification de la conservation des volumes BAAC apres nettoyage."""

from commun.recuperer_donnees import charger_tout
from wp2_nettoyage.pipeline import donnees_propres


def test_conservation_volumes():
    tables_brutes = charger_tout()
    tables_propres = donnees_propres()

    familles = ("caracteristiques", "lieux", "usagers", "vehicules")

    for famille in familles:
        assert famille in tables_brutes
        assert famille in tables_propres

        volume_brut = len(tables_brutes[famille])
        volume_propre = len(tables_propres[famille])

        assert volume_propre == volume_brut, (
            f"{famille} : {volume_brut} lignes brutes, "
            f"{volume_propre} lignes apres nettoyage"
        )
