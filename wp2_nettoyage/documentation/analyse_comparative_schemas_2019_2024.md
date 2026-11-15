# WP2-03 - Analyse comparative des schemas BAAC 2019-2024

## 1. Objet

Comparer les schemas des quatre familles BAAC entre 2019 et 2024 et documenter les tables et colonnes finales de propre pour validation par WP3.

## 2. Differences entre millesimes

- caracteristiques : Accident_Id en 2022 remplace Num_Acc dans les donnees brutes ; harmonisation en num_acc au chargement.
- usagers : id_usager absent des fichiers bruts 2019 et 2020, present a partir de 2021.
- lieux : plusieurs enregistrements possibles pour un meme accident, notamment depuis 2023.
- Une colonne annee est ajoutee lors du chargement de chaque famille.

## 2.1. Matrice comparative des colonnes brutes (2019-2024)

Source : metadata/profilage/profilage_brut_colonnes.csv.
Oui = colonne presente dans le fichier brut du millesime ; ? = absente.

| Table | Colonne brute | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| caracteristiques | Accident_Id | Non | Non | Non | Oui | Non | Non |
| caracteristiques | Num_Acc | Oui | Oui | Oui | Non | Oui | Oui |
| caracteristiques | adr | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | agg | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | an | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | atm | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | col | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | com | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | dep | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | hrmn | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | int | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | jour | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | lat | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | long | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | lum | Oui | Oui | Oui | Oui | Oui | Oui |
| caracteristiques | mois | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | Num_Acc | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | catr | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | circ | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | infra | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | larrout | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | lartpc | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | nbv | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | plan | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | pr | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | pr1 | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | prof | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | situ | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | surf | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | v1 | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | v2 | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | vma | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | voie | Oui | Oui | Oui | Oui | Oui | Oui |
| lieux | vosp | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | Num_Acc | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | actp | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | an_nais | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | catu | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | etatp | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | grav | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | id_usager | Non | Non | Oui | Oui | Oui | Oui |
| usagers | id_vehicule | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | locp | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | num_veh | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | place | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | secu1 | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | secu2 | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | secu3 | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | sexe | Oui | Oui | Oui | Oui | Oui | Oui |
| usagers | trajet | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | Num_Acc | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | catv | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | choc | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | id_vehicule | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | manv | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | motor | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | num_veh | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | obs | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | obsm | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | occutc | Oui | Oui | Oui | Oui | Oui | Oui |
| vehicules | senc | Oui | Oui | Oui | Oui | Oui | Oui |


## 3. Inventaire des tables finales de propre

Source : execution locale de wp2_nettoyage.pipeline.donnees_propres().

### caracteristiques

327628 lignes ; 21 colonnes.

| Colonne | Type pandas |
|---|---|
| num_acc | str |
| jour | Int64 |
| mois | Int64 |
| an | Int64 |
| hrmn | string |
| lum | Int64 |
| dep | str |
| com | str |
| agg | Int64 |
| int | Int64 |
| atm | Int64 |
| col | Int64 |
| adr | string |
| lat | Float64 |
| long | Float64 |
| annee | int64 |
| date_accident | datetime64[us] |
| heure_accident | string |
| datetime_accident | datetime64[us] |
| coordonnees_suspectes | boolean |
| metropole | bool |

### lieux

359512 lignes ; 21 colonnes.

| Colonne | Type pandas |
|---|---|
| num_acc | str |
| catr | Int64 |
| voie | string |
| v1 | string |
| v2 | string |
| circ | Int64 |
| nbv | Int64 |
| vosp | Int64 |
| prof | Int64 |
| pr | string |
| pr1 | string |
| plan | Int64 |
| lartpc | Float64 |
| larrout | Float64 |
| surf | Int64 |
| infra | Int64 |
| situ | Int64 |
| vma | Int64 |
| annee | int64 |
| vma_suspecte | boolean |
| lieu_principal | bool |

### usagers

745158 lignes ; 18 colonnes.

| Colonne | Type pandas |
|---|---|
| num_acc | str |
| id_vehicule | str |
| num_veh | str |
| place | Int64 |
| catu | Int64 |
| grav | Int64 |
| sexe | Int64 |
| an_nais | Int64 |
| trajet | Int64 |
| secu1 | Int64 |
| secu2 | Int64 |
| secu3 | Int64 |
| locp | Int64 |
| actp | string |
| etatp | Int64 |
| annee | int64 |
| id_usager | str |
| doublon_suspect | bool |

### vehicules

559847 lignes ; 12 colonnes.

| Colonne | Type pandas |
|---|---|
| num_acc | str |
| id_vehicule | str |
| num_veh | str |
| senc | Int64 |
| catv | Int64 |
| obs | Int64 |
| obsm | Int64 |
| choc | Int64 |
| manv | Int64 |
| motor | Int64 |
| occutc | Int64 |
| annee | int64 |


## 4. Regles importantes pour WP3

- Cle accident : num_acc.
- Jointure vehicules/usagers : num_acc et id_vehicule.
- Pour une jointure accident/lieux sans multiplication des accidents : filtrer lieu_principal == True.
- Pour compter les accidents : COUNT(DISTINCT num_acc).
- Les valeurs manquantes de id_usager pour 2019-2020 doivent etre prises en compte.

## 5. Validation WP3

**Statut : en attente de validation par WP3.**

Points a valider : noms et types des colonnes, cles de jointure, traitement des valeurs manquantes, colonnes obligatoires et modalites de livraison.

