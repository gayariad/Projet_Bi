"""Crée les schémas, les comptes et les droits sur la base Neon (compte admin)."""
import os
from urllib.parse import urlsplit, unquote

import psycopg
from psycopg import sql
from dotenv import load_dotenv

load_dotenv()

ANNEES = range(2019, 2025)
SCHEMAS_BRUT = [f"brut_{a}" for a in ANNEES]
SCHEMAS = SCHEMAS_BRUT + ["entrepot", "protocole"]
COMPTES = {
    "lecture": "URL_LECTURE",
    "chargement_wp2": "URL_CHARGEMENT_WP2",
    "etl_wp3": "URL_ETL_WP3",
}


def ident(*noms):
    return sql.SQL(", ").join(sql.Identifier(n) for n in noms)


def main():
    url_admin = os.environ["URL_ADMIN"]
    base = urlsplit(url_admin).path.lstrip("/")
    with psycopg.connect(url_admin, autocommit=True) as conn:
        cur = conn.cursor()

        for s in SCHEMAS:
            cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(s)))

        for role, cle in COMPTES.items():
            mdp = unquote(urlsplit(os.environ[cle]).password)
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,))
            verbe = "ALTER" if cur.fetchone() else "CREATE"
            cur.execute(sql.SQL(verbe + " ROLE {} LOGIN PASSWORD {}").format(
                sql.Identifier(role), sql.Literal(mdp)))

        cur.execute(sql.SQL("GRANT {} TO neondb_owner").format(ident("chargement_wp2", "etl_wp3")))

        tous = ident(*COMPTES)
        cur.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(sql.Identifier(base), tous))
        cur.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(ident(*SCHEMAS), tous))
        cur.execute(sql.SQL("GRANT CREATE ON SCHEMA {} TO chargement_wp2").format(ident(*SCHEMAS_BRUT)))
        cur.execute(sql.SQL("GRANT CREATE ON SCHEMA entrepot, protocole TO etl_wp3"))

        cur.execute(sql.SQL(
            "ALTER DEFAULT PRIVILEGES FOR ROLE chargement_wp2 IN SCHEMA {} "
            "GRANT SELECT ON TABLES TO lecture, etl_wp3").format(ident(*SCHEMAS_BRUT)))
        cur.execute(
            "ALTER DEFAULT PRIVILEGES FOR ROLE etl_wp3 IN SCHEMA entrepot, protocole "
            "GRANT SELECT ON TABLES TO lecture")

        cur.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")

        cur.execute("""
            SELECT pg_get_userbyid(d.defaclrole), n.nspname, d.defaclacl::text
            FROM pg_default_acl d JOIN pg_namespace n ON n.oid = d.defaclnamespace
            ORDER BY 2""")
        for ligne in cur.fetchall():
            print("default privileges:", *ligne)
    print("Schémas, comptes et droits en place.")


if __name__ == "__main__":
    main()
