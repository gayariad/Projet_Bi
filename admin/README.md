# admin : scripts réservés à l'administrateur de la base

**Ces scripts ne servent qu'à l'admin.** Les autres membres n'en ont pas besoin et n'ont pas
les comptes nécessaires.

| Script | Rôle | Variables `.env` |
|---|---|---|
| `setup_droits.py` | crée les schémas `brut_2019..2024`, `entrepot`, `protocole`, les comptes `lecture`, `chargement_wp2`, `etl_wp3` et leurs droits | `URL_ADMIN`, `URL_LECTURE`, `URL_CHARGEMENT_WP2`, `URL_ETL_WP3` |
| `charger_brut.py` | charge les CSV `raw/<annee>/*.csv` dans `brut_<annee>` (tout en texte, tables remplacées) | `URL_CHARGEMENT_WP2` |
| `verifier.py` | compare les lignes chargées à `raw/sources_inventory.csv`, affiche la taille de la base, teste les droits du compte `lecture` | `URL_ADMIN`, `URL_LECTURE` |

- Toutes les URL sont lues dans un `.env` (jamais en dur). Celles passées à psycopg directement
  (`URL_ADMIN`) sont au format `postgresql://...`.
- Les CSV ne sont pas dans le repo : lancer les scripts depuis le dossier qui contient `raw/`,
  ou indiquer son chemin avec la variable `DOSSIER_RAW`.
