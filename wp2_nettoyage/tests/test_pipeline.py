import os

import pytest
from dotenv import load_dotenv

from commun.recuperer_donnees import FAMILLES, RACINE

load_dotenv(RACINE / ".env")

pytestmark = pytest.mark.skipif(not os.environ.get("URL_LECTURE"), reason="pas de .env (URL_LECTURE)")


def test_donnees_propres_renvoie_4_tables_non_vides():
    from wp2_nettoyage.pipeline import donnees_propres

    t = donnees_propres()
    assert set(t) == set(FAMILLES)
    for famille, df in t.items():
        assert len(df) > 0, f"{famille} est vide"
