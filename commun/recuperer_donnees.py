"""Récupère les tables brutes BAAC (tous les schémas brut_AAAA) en DataFrames, avec cache parquet.

Usage :
    from commun.recuperer_donnees import charger_tout
    t = charger_tout()            # {"caracteristiques": df, "lieux": df, "usagers": df, "vehicules": df}

    python -m commun.recuperer_donnees [--rafraichir]
"""
import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

RACINE = Path(__file__).resolve().parents[1]
CACHE = RACINE / "cache"
FAMILLES = ["caracteristiques", "lieux", "usagers", "vehicules"]


def creer_engine(variable="URL_LECTURE"):
    """Engine SQLAlchemy depuis le .env à la racine du repo (créé à la demande, pas à l'import)."""
    load_dotenv(RACINE / ".env")
    url = os.environ.get(variable)
    if not url:
        raise RuntimeError(f"{variable} absente : copiez .env.exemple en .env à la racine du repo.")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(url)


def schemas_bruts(engine, famille):
    requete = text("""
        SELECT table_schema FROM information_schema.tables
        WHERE table_schema ~ '^brut_[0-9]{4}$' AND table_name = :famille
        ORDER BY table_schema""")
    with engine.connect() as conn:
        return [r[0] for r in conn.execute(requete, {"famille": famille})]


def lire_famille(engine, famille):
    morceaux = []
    for schema in schemas_bruts(engine, famille):
        df = pd.read_sql_query(text(f'SELECT * FROM "{schema}"."{famille}"'), engine)
        df = df.rename(columns={"accident_id": "num_acc"})  # 2022 : Accident_Id au lieu de Num_Acc
        df["annee"] = int(schema.removeprefix("brut_"))
        morceaux.append(df)
    if not morceaux:
        raise RuntimeError(f"Aucune table brut_AAAA.{famille} trouvée.")
    return pd.concat(morceaux, ignore_index=True)


def charger_tout(rafraichir=False):
    """Renvoie un dict {famille: DataFrame} ; lit le cache parquet sauf si rafraichir=True."""
    CACHE.mkdir(exist_ok=True)
    engine = None
    tables = {}
    for famille in FAMILLES:
        fichier = CACHE / f"{famille}.parquet"
        if fichier.exists() and not rafraichir:
            tables[famille] = pd.read_parquet(fichier)
            continue
        engine = engine or creer_engine()
        tables[famille] = lire_famille(engine, famille)
        tables[famille].to_parquet(fichier, index=False)
    if engine is not None:
        engine.dispose()
    return tables


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rafraichir", action="store_true", help="relire la base au lieu du cache")
    args = parser.parse_args()

    tables = charger_tout(rafraichir=args.rafraichir)
    total = 0
    for famille, df in tables.items():
        annees = sorted(df["annee"].unique())
        print(f"{famille:<17}{len(df):>10} lignes  {df.shape[1]:>3} colonnes  années {annees[0]}-{annees[-1]} ({len(annees)})")
        total += len(df)
    print(f"{'total':<17}{total:>10} lignes")


if __name__ == "__main__":
    main()
