# Projet BI : accidents corporels de la route (BAAC 2019-2024)

Analyse des accidents corporels de la circulation en France à partir des fichiers annuels BAAC
(data.gouv.fr) : nettoyage, entrepôt en étoile, tableaux de bord Power BI, analyses.

```
commun/recuperer_donnees.py    charger_tout() : tables brutes -> DataFrames (cache parquet)
wp2_nettoyage/                 pipeline.py + etapes/eNNN_*.py
wp3_entrepot/construire.py     construction du schéma entrepot
wp4_dashboards/                projet Power BI (.pbip)
wp5_analyses/ … wp7_analyses/  analyses (exemple.py)
```

## 1. Ce qu'il y a dans la base

Base PostgreSQL `neondb` hébergée sur Neon.

| Schéma | Contenu |
|---|---|
| `brut_2019` … `brut_2024` | 4 tables par année, **tout en texte**, telles que dans les CSV : `caracteristiques`, `lieux`, `usagers`, `vehicules` |
| `entrepot` | schéma en étoile (dimensions + faits) construit par le WP3 |
| `protocole` | découpage train/test commun à toutes les analyses |

Au total 1 992 145 lignes brutes, dont 745 158 usagers.

## 2. Installation

```bash
git clone git@github.com:gayariad/Projet_Bi.git && cd Projet_Bi
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.exemple .env               # Windows : copy .env.exemple .env
```

Dans `.env`, remplacez la ligne `URL_LECTURE=...` par l'URL reçue **en privé**.
`.env` est ignoré par git. Toutes les commandes se lancent **depuis la racine du repo** avec `python -m`.

## 3. Se connecter

L'URL reçue a la forme `postgresql+psycopg://lecture:MOTDEPASSE@HOTE/neondb?sslmode=require`.
Le compte `lecture` lit tout et ne peut rien modifier. Ne partagez jamais cette URL.

- **DBeaver** : Nouvelle connexion > PostgreSQL. Hôte `HOTE`, port `5432`, base `neondb`,
  utilisateur `lecture`, mot de passe `MOTDEPASSE`. Onglet SSL : activer, mode **require**. Tester, puis Terminer.
- **Python** :
  ```python
  from commun.recuperer_donnees import charger_tout
  t = charger_tout()                 # {"caracteristiques", "lieux", "usagers", "vehicules"}
  ```
  Le premier appel lit la base et crée le cache `cache/`. Ensuite : `charger_tout(rafraichir=True)`
  pour relire la base. Vérification rapide : `python -m commun.recuperer_donnees`.
- **Power BI Desktop** : Obtenir les données > Base de données PostgreSQL. Serveur `HOTE`, base `neondb`,
  mode Importer. Identifiants : onglet Base de données, `lecture` / `MOTDEPASSE`. Garder le chiffrement.

## 4. Comment on travaille

- Une branche par tâche (`git switch -c wp2-types`), puis push de la branche et **pull request** vers `main`.
- **Pas de push direct sur `main`.**
- **Jamais de `.env`, de mot de passe ni de données** (CSV, parquet, xlsx, sorties de notebooks) sur GitHub :
  le dépôt est public. Vérifiez `git status` avant chaque commit.
- **Personne ne modifie la base à la main.** `entrepot` n'est écrit que par `wp3_entrepot/construire.py`.

## 5. Les work packages

**WP2 : nettoyage.** `donnees_propres()` (`wp2_nettoyage/pipeline.py`) lit les tables brutes avec
`charger_tout()` puis applique dans l'ordre les étapes listées dans `ORDRE`. Une étape est un fichier
`wp2_nettoyage/etapes/eNNN_nom.py` qui expose `appliquer(t: dict) -> dict` (modèle : `e100_exemple.py`).
Pour en ajouter une : créer le fichier, puis ajouter son nom dans `ORDRE`.

**WP3 : entrepôt.** `python -m wp3_entrepot.construire` lit `donnees_propres()`, construit les dimensions et
les faits (TODO dans le fichier), les écrit dans `entrepot` (tables remplacées) et ajoute `entrepot.version`
(date et hash du commit). Il nécessite `URL_ETL_WP3` dans `.env`, fourni en privé à la personne du WP3. Les tables
créées sont automatiquement lisibles par le compte `lecture`.

**WP4 : tableaux de bord.** Projet Power BI au format `.pbip` dans `wp4_dashboards/` (pas de `.pbix`),
branché sur le schéma `entrepot` avec le compte `lecture`. Les identifiants restent dans Power BI Desktop.

**WP5 à WP7 : analyses.** Chaque dossier contient un `exemple.py` (`python -m wp5_analyses.exemple`) qui
charge `donnees_propres()` et compte les usagers par gravité et par année. Utilisez les données nettoyées du WP2
et le découpage du schéma `protocole`, pour que les résultats soient comparables.
