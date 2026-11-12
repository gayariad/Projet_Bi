# WP2 — Préparation & Qualité des Données BAAC (2019–2024)

Ce dossier contient l'intégralité du pipeline de données, des scripts d'harmonisation, des contrôles de qualité, de la batterie de tests et des métadonnées du **Work Package 2 (WP2)** pour le projet d'analyse décisionnelle des accidents corporels de la circulation en France.

---

## 🏗️ Structure du Répertoire `wp2_nettoyage`

```text
wp2_nettoyage/
├── README.md                          --> Ce guide principal
├── pipeline.py                        --> Script maître d'exécution du pipeline
├── documentation/                     --> Documents de cadrage, limites et contrats d'interface
│   ├── note_cadrage_wp2.md
│   ├── rapport_technique_wp2.md
│   ├── contrat_interface_wp2_wp3.md
│   └── limites_et_versions_baac.md
├── metadata/                          --> Registres, profilage et métadonnées
│   ├── codifications/                 --> Dictionnaire (64 variables) et modalites
│   │   ├── dictionnaire_baac_complet.csv
│   │   └── modalites_baac_finalisees.csv
│   ├── nettoyage/                     --> Registre officiel des règles (R001–R008)
│   │   └── registre_regles.csv
│   ├── profilage/                     --> Rapports d'incomplétude, doublons et valeurs spéciales
│   └── qualite/                       --> Bilans des tests et contrôles métiers
├── scripts/ & etapes/                 --> Scripts Python d'automatisation
└── tests/                             --> Suite de tests automatisés (unitaires & intégration)
```

---

## 🚀 Exécution du Pipeline

### Préréquis
Assurez-vous d'avoir Python 3.10+ installé ainsi que les dépendances nécessaires :
```bash
pip install -r requirements.txt
```

### Option A : Exécution globale via le Pipeline Master
Pour exécuter l'ensemble de la chaîne de traitement (téléchargement, harmonisation, profilage et génération des métadonnées) :
```bash
python -c 'from wp2_nettoyage.pipeline import donnees_propres; print({k: len(v) for k, v in donnees_propres().items()})'
```

### Option B : Exécution étape par étape
Les étapes principales peuvent être lancées séparément :
1. **Téléchargement des sources RAW (2019–2024)** :
   ```bash
   python scripts/wp2_download_baac_corrige.py
   ```
2. **Harmonisation Silver** :
   ```bash
   python scripts/harmoniser_baac.py
   ```
3. **Profilage et génération des métadonnées** :
   ```bash
   python scripts/profiler_baac.py
   ```
4. **Préparation du plan de nettoyage** :
   ```bash
   python scripts/preparer_regles_nettoyage_wp2.py
   ```

---

## 🧪 Lancement des Tests & Contrôles Qualité

Avant toute livraison aux équipes consommatrices (WP3), l'ensemble de la suite de contrôles doit être validé sans erreur.

### 1. Contrôles de structure & d'intégration (12 tests)
```bash
python scripts/tester_qualite_avant_nettoyage.py
```

### 2. Contrôles métiers & cohérence calendaire (58 contrôles)
```bash
python scripts/controle_metier_avant_nettoyage.py
```

### 3. Exécution via Pytest
```bash
python -m pytest wp2_nettoyage/tests/ -q
```

---

## 📋 Règles de Nettoyage Validées (`propre_v2`)

Les règles validées lors des arbitrages inter-équipes pour la version `propre_v2` sont consignées dans `metadata/nettoyage/registre_regles.csv` :
* **R001** : Renommage d'`Accident_Id` (2022) en `Num_Acc`.
* **R002** : Conservation de `id_usager` vide pour 2019–2020 sans invention de faux identifiants.
* **R003** : Conversion des `-1` de `larrout` en `NA` (information non renseignée).
* **R004** : Normalisation des marqueurs d'absence hétérogènes de `v2` en `pd.NA`.
* **R005** : Conservation de `lartpc` (99,84% de vides) avec documentation de son taux d'incomplétude.
* **R006** : Distinction "sans objet" / `NA` sur `occutc` selon la catégorie de véhicule (`catv`).
* **R007** : Conservation des 164 doublons usagers ambigus avec ajout d'une colonne booléenne `doublon_suspect` (299 lignes signalées).
* **R008** : Maintien de la cardinalité multiple sur `Num_Acc` dans la table `lieux` (2023–2024).

---

## 📊 Accès aux Données & Livrables

1. **Données Consolidées (Locales / GitHub LFS)** :
   * Zone Silver : `data/silver/` (4 fichiers CSV, ~1,99 million de lignes).
2. **Base de Données PostgreSQL / Neon** :
3. **Dictionnaire de Données** :
   * Consulter `metadata/codifications/dictionnaire_baac_complet.csv` ou le document `documentation/contrat_interface_wp2_wp3.md`.

---

## 👥 Contacts & Responsabilités WP2

* **Pilotage & Coordination** : Mohamed Reda Lahmar
* **Documentation & Dictionnaire** : Lucas Edouard / Febbe Kiazi Tsaka Ngoma
* **Dépôt GitHub** : [gayariad/Projet_Bi](https://github.com/gayariad/Projet_Bi)
## Interface reelle et precisions de livraison

Depuis la racine du depot :

    from wp2_nettoyage.pipeline import donnees_propres
    tables = donnees_propres()

La fonction retourne quatre DataFrames pandas :
caracteristiques, lieux, usagers et vehicules.

Tests :

    py -m pytest wp2_nettoyage/tests/ -q

R006 : occutc est conservee. Son interpretation depend
de catv afin de distinguer les cas sans objet des valeurs
non renseignees. Aucune imputation automatique.

R008 : toutes les lignes de lieux sont conservees.
lieu_principal identifie exactement une ligne de reference
par accident, sans supprimer les autres lignes.

La version propre_v2 reste candidate jusqu'a validation
finale et fusion dans main.