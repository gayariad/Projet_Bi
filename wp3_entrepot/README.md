# WP3 : entrepôt

`construire.py` lit `donnees_propres()` (WP2), construit les dimensions et les faits du schéma
en étoile, puis les écrit dans le schéma `entrepot` (remplacement complet), avec une table
`entrepot.version` (date de construction + hash du commit git).

- Nécessite `URL_ETL_WP3` dans `.env` (compte `etl_wp3`, fourni en privé à la personne du WP3).
- Lancement : `python -m wp3_entrepot.construire` depuis la racine du repo.
- `sql/` : requêtes SQL utiles (vues, contrôles), versionnées ici.
- Les tables créées par `etl_wp3` sont automatiquement lisibles par le compte `lecture`.
