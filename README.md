# Projet BI : accidents corporels de la route (BAAC 2019-2024)

Analyse des accidents corporels de la circulation routière en France, à partir des
fichiers annuels BAAC publiés sur data.gouv.fr (années 2019 à 2024) : nettoyage,
entrepôt en étoile, tableaux de bord Power BI et analyses.

## Contenu de la base (PostgreSQL hébergé sur Neon, base `neondb`)

| Schéma | Contenu |
|---|---|
| `brut_2019` … `brut_2024` | 4 tables par année, **tout en texte**, telles que dans les CSV : `caracteristiques`, `lieux`, `usagers`, `vehicules` |
| `entrepot` | Schéma en étoile (dimensions + faits) construit par le WP3 |
| `protocole` | Découpage train/test commun à toutes les analyses |

Volumes chargés : 1 992 145 lignes au total (dont 745 158 usagers).

## Arborescence

```
commun/                 code partagé : recuperer_donnees.charger_tout()
wp0_pilotage/           organisation, planning, comptes rendus
wp2_nettoyage/          pipeline de nettoyage (étapes eNNN_*.py) + tests
wp3_entrepot/           construction du schéma entrepot (construire.py, sql/)
wp4_dashboards/         projet Power BI (.pbip)
wp5_analyses/           notebooks d'analyse
wp6_analyses/           notebooks d'analyse
wp7_analyses/           notebooks d'analyse
admin/                  scripts d'administration de la base (réservés à l'admin)
docs/connexion.md       se connecter avec DBeaver, Python, Power BI
```

## Installation

```bash
git clone git@github.com:gayariad/Projet_Bi.git
cd Projet_Bi
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.exemple .env               # Windows : copy .env.exemple .env
```

Ouvrez ensuite `.env` et remplacez la ligne `URL_LECTURE=...` par l'URL reçue **en privé**.
Vérifiez avec :

```bash
python -m commun.recuperer_donnees   # affiche lignes et années par table
pytest
```

Les données sont mises en cache dans `cache/` (parquet). Pour les relire depuis la base :
`python -m commun.recuperer_donnees --rafraichir`.

## Règles

- **Jamais de `.env`, de mot de passe ni de données (CSV, parquet, xlsx…) sur GitHub.** Le dépôt est public.
  Le `.gitignore` les exclut ; vérifiez quand même `git status` avant chaque commit.
- **Pas de push direct sur `main`** : créez une branche, poussez-la, ouvrez une pull request.
- **Personne ne modifie la base à la main.** Le schéma `entrepot` n'est écrit que par
  `wp3_entrepot/construire.py` ; les schémas `brut_*` que par les scripts de `admin/`.
