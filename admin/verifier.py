"""Compare les lignes chargées à l'inventaire, affiche la taille de la base et teste le compte lecture."""
import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

from charger_brut import nom_table

load_dotenv()

RAW = Path(os.environ.get("DOSSIER_RAW", "raw"))  # dossier des CSV, hors du repo


def main():
    inv = pd.read_csv(RAW / "sources_inventory.csv", sep=";", encoding="latin-1", dtype=str)
    inv = inv.iloc[:, [0, 1, 5]].dropna()
    inv.columns = ["annee", "fichier", "lignes"]
    inv["attendu"] = inv["lignes"].str.replace(r"\D", "", regex=True).astype(int)

    ecarts = 0
    with psycopg.connect(os.environ["URL_ADMIN"]) as conn:
        print(f"{'table':<28}{'chargé':>10}{'inventaire':>12}  statut")
        for r in inv.itertuples():
            cible = f"brut_{r.annee}.{nom_table(Path(r.fichier))}"
            try:
                charge = conn.execute(f"SELECT count(*) FROM {cible}").fetchone()[0]
            except psycopg.Error as e:
                conn.rollback()
                charge, statut = None, f"ERREUR {e.diag.message_primary}"
            else:
                statut = "OK" if charge == r.attendu else f"ÉCART {charge - r.attendu:+d}"
            ecarts += statut != "OK"
            print(f"{cible:<28}{charge if charge is not None else '-':>10}{r.attendu:>12}  {statut}")
        print(f"\n{len(inv)} tables comparées, {ecarts} écart(s).")

        nom, taille = conn.execute(
            "SELECT current_database(), pg_size_pretty(pg_database_size(current_database()))").fetchone()
        print(f"Taille de la base {nom} : {taille}")

    print("\nTests du compte lecture :")
    with psycopg.connect(os.environ["URL_LECTURE"]) as conn:
        n = conn.execute("SELECT count(*) FROM brut_2024.usagers").fetchone()[0]
        print(f"  SELECT sur brut_2024.usagers : OK ({n} lignes)")
        for schema in ["brut_2024", "entrepot", "protocole", "public"]:
            try:
                conn.execute(f"CREATE TABLE {schema}.test_lecture (id int)")
                print(f"  CREATE TABLE dans {schema} : AUTORISÉ (problème !)")
            except psycopg.errors.InsufficientPrivilege as e:
                print(f"  CREATE TABLE dans {schema} : refusé comme attendu ({e.diag.message_primary})")
            finally:
                conn.rollback()


if __name__ == "__main__":
    main()
