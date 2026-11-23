# Conventions SQL WP3

Validées avec l'équipe WP3

## Règles générales

- Seul le script `wp3_entrepot/construire.py` écrit dans entrepot. On ne modifie rien à la main dans DBeaver.
- S'il faut corriger quelque chose : on modifie le script, on fait une PR, puis on relance.
- Tout le monde lit avec le compte lecture. Les URL restent dans le .env.

## Noms

- Tout en minuscules, avec des underscores, sans accents.
- Dimensions : `dim_...` (ex : dim_date)
- Faits : `fait_...` (ex : fait_usager)
- Vues : `v_...`
- Tables de libellés : `ref_...`
- Clé d'une dimension : `nom_id` (ex : date_id pour dim_date).
- Compteurs : `nb_...` (ex : nb_tues)
- On garde les noms BAAC pour les codes (catr, catv, grav, lum, atm...).

## Valeurs manquantes

Le WP2 a déjà mis les codes "non renseigné" à NULL. Dans l'entrepôt on laisse NULL, on ne remplace pas.
Dans Power BI on peut l'afficher "Non renseigné".

## Types

- Les codes département et commune restent en texte (2A, 2B, zéros devant).
- num_acc reste en texte.

## Écriture des requêtes

- Mots clés SQL en majuscules.
- Toujours mettre le schéma devant : `entrepot.nom_table`.
- Pas de SELECT * dans les vues.
- Attention au grain : pour compter des accidents, utiliser COUNT(DISTINCT num_acc) si la table a plusieurs lignes par accident.
