"""Découpage commun apprentissage/test (celui de preparation.py), stocké dans protocole.decoupage.

ensemble = lire_decoupage()                  # num_acc -> "apprentissage" / "test"
verifier_table_analyse(ta)                   # erreur si ta n'a pas ce découpage
python -m wp5_analyses.protocole [--complet]
python -m wp5_analyses.protocole --ecrire URL_ECRITURE [--remplacer]   # compte en écriture
"""

import argparse
import math
from datetime import date

import pandas as pd
from sqlalchemy import text

from commun.recuperer_donnees import creer_engine
from wp5_analyses.preparation import EMPREINTE_REFERENCE, GRAINE, PART_TEST, empreinte

SCHEMA = "protocole"
TABLE = "decoupage"
LECTEUR = "lecture"
APP, TEST = "apprentissage", "test"

CREATION = f"""
CREATE TABLE {SCHEMA}.{TABLE} (
    num_acc TEXT PRIMARY KEY,
    ensemble TEXT NOT NULL CHECK (ensemble IN ('{APP}', '{TEST}'))
)"""
LECTURE = f"SELECT num_acc, ensemble FROM {SCHEMA}.{TABLE}"


def decoupage_de(ta):
    ensemble = pd.concat(
        [pd.Series(APP, index=ta.X_app.index), pd.Series(TEST, index=ta.X_test.index)]
    )
    ensemble.index = ensemble.index.astype(str)
    return ensemble.rename("ensemble").rename_axis("num_acc").sort_index()


def calculer_decoupage(ta=None):
    if ta is None:
        from wp5_analyses.preparation import table_analyse

        ta = table_analyse()
    return decoupage_de(ta)


def controler(ensemble, reference=EMPREINTE_REFERENCE, part_test=PART_TEST):
    erreurs = []
    if ensemble.index.hasnans:
        erreurs.append("num_acc manquants")
    if not ensemble.index.is_unique:
        erreurs.append(f"{ensemble.index.duplicated().sum()} num_acc en double")
    inconnues = set(ensemble.dropna().unique()) - {APP, TEST}
    if ensemble.isna().any() or inconnues:
        erreurs.append(f"valeurs inattendues : {sorted(map(str, inconnues)) or 'vides'}")
    n_test = int(ensemble.eq(TEST).sum())
    attendu = math.ceil(len(ensemble) * part_test)
    if abs(n_test - attendu) > 1:
        erreurs.append(f"{n_test} accidents en test au lieu de {attendu} ({part_test:.0%})")
    valeur = empreinte(ensemble.index[ensemble.eq(TEST)])
    if reference is not None and valeur != reference:
        erreurs.append(f"empreinte du test {valeur} au lieu de {reference}")
    if erreurs:
        raise ValueError("Découpage invalide : " + " ; ".join(erreurs))
    return valeur


def comparer(ensemble, reference):
    manquants = reference.index.difference(ensemble.index)
    en_trop = ensemble.index.difference(reference.index)
    communs = reference.index.intersection(ensemble.index)
    changes = int((ensemble.loc[communs] != reference.loc[communs]).sum())
    if len(manquants) or len(en_trop) or changes:
        raise ValueError(
            f"Découpages différents : {len(manquants)} accidents manquants, "
            f"{len(en_trop)} en trop, {changes} changés d'ensemble."
        )


def lire_decoupage(variable="URL_LECTURE"):
    engine = creer_engine(variable)
    try:
        with engine.connect() as c:
            df = pd.read_sql_query(text(LECTURE), c)
    finally:
        engine.dispose()
    return df.set_index("num_acc")["ensemble"].sort_index()


def verifier_table_analyse(ta, ensemble=None):
    ensemble = lire_decoupage() if ensemble is None else ensemble
    comparer(decoupage_de(ta), ensemble)


def _preparer_schema(c):
    existe = c.execute(
        text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :s"), {"s": SCHEMA}
    ).first()
    if not existe:
        c.execute(text(f"CREATE SCHEMA {SCHEMA}"))
    acces = c.execute(
        text("SELECT has_schema_privilege(:u, :s, 'USAGE')"), {"u": LECTEUR, "s": SCHEMA}
    ).scalar()
    if not acces:
        c.execute(text(f"GRANT USAGE ON SCHEMA {SCHEMA} TO {LECTEUR}"))


def ecrire(variable, remplacer=False, ensemble=None):
    ensemble = calculer_decoupage() if ensemble is None else ensemble
    valeur = controler(ensemble)
    commentaire = (
        f"Découpage commun WP5/WP6/WP7 (wp5_analyses/preparation.py), part de test {PART_TEST}, "
        f"graine {GRAINE}, stratifié sur grave, métropole. "
        f"Empreinte du test {valeur}. Écrit le {date.today():%d/%m/%Y}."
    ).replace("'", "''")
    engine = creer_engine(variable)
    try:
        with engine.begin() as c:
            _preparer_schema(c)
            if remplacer:
                c.execute(text(f"DROP TABLE IF EXISTS {SCHEMA}.{TABLE}"))
            c.execute(text(CREATION))
            ensemble.reset_index().to_sql(
                TABLE,
                c,
                schema=SCHEMA,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=5000,
            )
            relu = pd.read_sql_query(text(LECTURE), c).set_index("num_acc")["ensemble"]
            comparer(relu, ensemble)
            controler(relu)
            c.execute(text(f"COMMENT ON TABLE {SCHEMA}.{TABLE} IS '{commentaire}'"))
            c.execute(text(f"GRANT SELECT ON {SCHEMA}.{TABLE} TO {LECTEUR}"))
    finally:
        engine.dispose()
    print(f"{SCHEMA}.{TABLE} écrite : {len(ensemble)} accidents, empreinte {valeur}")


def verifier(variable="URL_LECTURE", complet=False):
    ensemble = lire_decoupage(variable)
    valeur = controler(ensemble)
    effectifs = ensemble.value_counts()
    print(
        f"{SCHEMA}.{TABLE} : {effectifs.get(APP, 0)} {APP}, {effectifs.get(TEST, 0)} {TEST}, "
        f"empreinte {valeur} OK"
    )
    if complet:
        comparer(ensemble, calculer_decoupage())
        print("Identique au découpage recalculé par preparation.py : OK")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--ecrire", metavar="VARIABLE_URL", help="variable du .env avec l'URL en écriture"
    )
    parser.add_argument(
        "--remplacer", action="store_true", help="supprime la table existante avant"
    )
    parser.add_argument(
        "--complet", action="store_true", help="compare aussi avec le découpage recalculé"
    )
    args = parser.parse_args()
    if args.ecrire:
        ecrire(args.ecrire, args.remplacer)
    else:
        verifier(complet=args.complet)


if __name__ == "__main__":
    main()
