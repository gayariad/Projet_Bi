"""Construit le schéma entrepot (étoile) à partir des données nettoyées du WP2.

Squelette à compléter par le WP3. Écrit avec le compte etl_wp3 (URL_ETL_WP3 dans .env),
seul compte autorisé à créer des tables dans entrepot.

    python -m wp3_entrepot.construire
"""
import subprocess
from datetime import datetime, timezone

import pandas as pd

from commun.recuperer_donnees import RACINE, creer_engine
from wp2_nettoyage.pipeline import donnees_propres

SCHEMA = "entrepot"


def construire_dimensions(t):
    """Renvoie un dict {nom_table: DataFrame} de dimensions."""
    dims = {}
    # TODO dim_date : une ligne par jour (date, jour, mois, année, jour de semaine, heure ?)
    # TODO dim_lieu : département, commune, agglomération, catégorie de route…
    # TODO dim_conditions : luminosité, météo, type de collision…
    # TODO dim_vehicule : catégorie de véhicule, motorisation…
    # TODO dim_usager : catégorie, sexe, tranche d'âge, équipement de sécurité…
    return dims


def construire_faits(t, dims):
    """Renvoie un dict {nom_table: DataFrame} de faits."""
    faits = {}
    # TODO fait_usager : une ligne par usager impliqué (grain le plus fin), clés vers les dimensions,
    #      mesures : gravité (tué, hospitalisé, blessé léger, indemne)
    # TODO fait_accident ? agrégat par accident (nb véhicules, nb usagers, nb tués…)
    return faits


def hash_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=RACINE, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "inconnu"


def main():
    t = donnees_propres()
    dims = construire_dimensions(t)
    faits = construire_faits(t, dims)

    engine = creer_engine("URL_ETL_WP3")
    for nom, df in {**dims, **faits}.items():
        df.to_sql(nom, engine, schema=SCHEMA, if_exists="replace", index=False, chunksize=50_000)
        print(f"{SCHEMA}.{nom} : {len(df)} lignes")

    version = pd.DataFrame([{"date": datetime.now(timezone.utc), "commit": hash_commit()}])
    version.to_sql("version", engine, schema=SCHEMA, if_exists="replace", index=False)
    engine.dispose()


if __name__ == "__main__":
    main()
