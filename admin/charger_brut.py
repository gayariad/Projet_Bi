"""Charge les CSV BAAC de raw/<annee>/ dans brut_<annee>, tout en texte (compte chargement_wp2)."""
import csv
import io
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

RAW = Path(os.environ.get("DOSSIER_RAW", "raw"))  # dossier des CSV, hors du repo
TABLES = {"car": "caracteristiques", "lieux": "lieux", "usagers": "usagers", "vehicules": "vehicules"}


def nom_table(fichier: Path) -> str:
    nom = fichier.name.lower()
    for prefixe, table in TABLES.items():
        if nom.startswith(prefixe):
            return table
    raise ValueError(f"Fichier non reconnu : {fichier}")


def copy_postgres(table, conn, keys, data_iter):
    """Méthode d'insertion pour to_sql : COPY, bien plus rapide que des INSERT."""
    buf = io.StringIO()
    csv.writer(buf).writerows(data_iter)
    buf.seek(0)
    colonnes = ", ".join(f'"{k}"' for k in keys)
    cible = f'"{table.schema}"."{table.name}"' if table.schema else f'"{table.name}"'
    with conn.connection.cursor() as cur:
        with cur.copy(f"COPY {cible} ({colonnes}) FROM STDIN WITH (FORMAT csv)") as copy:
            copy.write(buf.getvalue())


def main():
    url = os.environ["URL_CHARGEMENT_WP2"].replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_engine(url)
    for dossier in sorted(p for p in RAW.iterdir() if p.is_dir() and p.name.isdigit()):
        schema = f"brut_{dossier.name}"
        for fichier in sorted(dossier.glob("*.csv")):
            table = nom_table(fichier)
            # keep_default_na=False : on garde le texte brut ("", "N/A"...) sans le changer en NULL
            df = pd.read_csv(fichier, sep=";", encoding="utf-8", dtype=str, keep_default_na=False)
            df.columns = [c.strip().lower() for c in df.columns]
            df.to_sql(table, engine, schema=schema, if_exists="replace", index=False,
                      method=copy_postgres, chunksize=50_000)
            print(f"{schema}.{table:<16} <- {fichier.name:<26} {len(df):>8} lignes")
    engine.dispose()


if __name__ == "__main__":
    main()
