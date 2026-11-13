# WP2 - Preparation et qualite des donnees BAAC (2019-2024)

## 1. Objectif

Le WP2 prepare et controle les donnees BAAC 2019-2024 pour leur exploitation par les autres Work Packages, notamment le WP3.

Le pipeline charge les tables depuis la source de donnees du projet, applique les regles de nettoyage validees et retourne quatre DataFrames pandas.

Il n'est pas necessaire de relancer les anciens scripts de telechargement pour utiliser ce pipeline.

## 2. Prerequis

- Python et les dependances du projet
- Acces a la base PostgreSQL configuree pour le projet
- Execution depuis la racine du depot Projet_Bi

Installer les dependances :

```bash
python -m pip install -r requirements.txt
```

La connexion aux donnees est assuree par `commun.recuperer_donnees.charger_tout()`. La configuration de cette connexion doit etre operationnelle avant l'execution.

## 3. Executer le pipeline

Depuis la racine du depot :

```python
from wp2_nettoyage.pipeline import donnees_propres

tables = donnees_propres()

for nom, df in tables.items():
    print(nom, len(df))
```

Sur Windows, pour lancer directement cet exemple dans PowerShell :

```powershell
py -c "from wp2_nettoyage.pipeline import donnees_propres; print({k: len(v) for k, v in donnees_propres().items()})"
```

La fonction retourne un dictionnaire contenant :

- `caracteristiques`
- `lieux`
- `usagers`
- `vehicules`

Ces tables sont des DataFrames pandas. La fonction n'exporte pas automatiquement de nouveaux fichiers CSV.

## 4. Etapes du nettoyage

L'ordre des transformations est defini dans `wp2_nettoyage/pipeline.py`.

| Etape | Traitement |
| --- | --- |
| e100 | Etape d'exemple, sans transformation |
| e110 | Harmonisation des donnees |
| e115 | Typage des colonnes |
| e120 | Traitement des codes de valeurs manquantes selon le referentiel |
| e125 | Signalement des valeurs hors plage |
| e130 | Indicateur metropole |
| e140 | Identification des doublons suspects |
| e150 | Identification du lieu principal par accident |

Les lignes ne sont pas supprimees automatiquement pour les anomalies signalees par les indicateurs de qualite.

## 5. Tests

Depuis la racine du depot :

```powershell
py -m pytest wp2_nettoyage/tests/ -q
```

Derniere validation technique avant livraison :
34 tests reussis.

Cette validation technique ne remplace pas la revue et l'approbation de la Pull Request.

## 6. Regles et points de vigilance

Les decisions de nettoyage sont decrites dans :

- `wp2_nettoyage/metadata/nettoyage/registre_regles.csv`
- `wp2_nettoyage/metadata/nettoyage/codes_manquants.csv`

Principaux points d'attention :

- `occutc` est conserve sans imputation automatique ; son interpretation depend notamment de `catv`.
- `doublon_suspect` permet de reperer les lignes d'usagers suspectes sans les supprimer.
- La table `lieux` conserve sa cardinalite d'origine.
- `lieu_principal` identifie une ligne de reference par accident.
- Pour `pr` et `pr1`, le marqueur `(1)` des annees 2019-2022 est normalise selon les regles du pipeline.

Certaines modalites ONISR necessitent encore une confirmation documentaire :

- `v1 = -1` : interpretation a confirmer.
- `nbv = 0` : interpretation a confirmer.
- `actp = 7/8` : correspondance avec les definitions historiques a confirmer.

Ces valeurs sont conservees lorsqu'aucune transformation n'est suffisamment justifiee. Les WP consommateurs doivent tenir compte de ces reserves dans leurs indicateurs.

## 7. Interface avec les autres WP

Le contrat d'interface est disponible dans :

`wp2_nettoyage/documentation/contrat_interface_wp2_wp3.md`

Pour une analyse necessitant exactement un lieu par accident, utiliser la colonne `lieu_principal` de la table `lieux`.

Ne pas supposer que toutes les tables ont une seule ligne par `num_acc`.

## 8. Documentation

- `documentation/` : cadrage, rapport technique, limites et contrat WP2-WP3
- `metadata/codifications/` : dictionnaire et modalites BAAC
- `metadata/nettoyage/` : regles de nettoyage
- `tests/` : tests automatises
- `etapes/` : transformations du pipeline

Les chemins ci-dessus sont relatifs au dossier `wp2_nettoyage/`.

## 9. Etat de livraison

La version `propre_v2` a passe la validation technique avec 34 tests reussis.

Elle reste une version candidate jusqu'a l'approbation et la fusion de la Pull Request dans `main`.

Depot : https://github.com/gayariad/Projet_Bi
