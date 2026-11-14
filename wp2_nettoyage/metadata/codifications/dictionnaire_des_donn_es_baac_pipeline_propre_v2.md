# Dictionnaire des Données BAAC — Pipeline `propre_v2`

> **Note méthodologique :** L'ensemble des variables, typages, règles de gestion et volumétries présentés dans ce dictionnaire reflètent l'état exact des tables en sortie de la fonction `donnees_propres()` (**après exécution du pipeline de nettoyage `propre_v2`**).

---

## Vue d'ensemble des tables

| Table | Description | Clé primaire / Jointure | Nb. de variables |
| :--- | :--- | :--- | :---: |
| **`caracteristiques`** | Circonstances générales, date, heure et localisation de l'accident | `num_acc` (Unique) | 20 |
| **`lieux`** | Description de l'infrastructure routière sur le lieu de l'accident | `num_acc` (1:1 via `lieu_principal`) | 20 |
| **`vehicules`** | Caractéristiques des véhicules impliqués dans l'accident | `num_acc` + `id_vehicule` | 11 |
| **`usagers`** | Profil, statut et gravité des personnes impliquées | `num_acc` + `id_vehicule` + `id_usager` | 17 |

---

## 1. Table `caracteristiques`

| Variable | Type | Description & Modalités | Règles de nettoyage & Notes (`propre_v2`) |
| :--- | :--- | :--- | :--- |
| **`num_acc`** | `str` | Identifiant unique de l'accident sur 12 caractères (`AAAANNNNNNNN`). | Harmonisé en minuscules dans les 4 tables (nommé `Accident_Id` dans le fichier brut 2022). |
| **`an`** | `int` | Année de l'accident au format 4 chiffres (`2019` à `2024`). | Conservé uniquement dans `caracteristiques` (ex-`an`). |
| **`mois`** | `int` | Mois de l'accident (`1` à `12`). | **12 valeurs distinctes** après harmonisation des formats bruts (`"1"` / `"01"`). |
| **`jour`** | `int` | Jour du mois (`1` à `31`). | Converti en entier. |
| **`hrmn`** | `str` | Heure et minutes de l'accident au format `HH:MM`. | Standardisé sur 5 caractères. |
| **`lum`** | `int` | Conditions d'éclairage (`1` : Plein jour, `2` : Crépuscule/aube, `3` : Nuit sans éclairage public, `4` : Nuit avec éclairage non allumé, `5` : Nuit avec éclairage allumé). | `-1` : Non renseigné. |
| **`dep`** | `str` | Code INSEE du département (`01` à `95`, `2A`, `2B`, `971` à `988`). | Harmonisé en chaîne de caractères (ex. maintien du `0` initial). |
| **`com`** | `str` | Code INSEE de la commune (département + code commune sur 5 caractères). | Harmonisé en chaîne de caractères. |
| **`agg`** | `int` | Localisation (`1` : Hors agglomération, `2` : En agglomération). | `-1` : Non renseigné. |
| **`int`** | `int` | Type d'intersection (`1` : Hors intersection, `2` : En X, `3` : En T, `4` : En Y, `5` : À plus de 4 branches, `6` : Giratoire, `7` : Place, `8` : Passage à niveau, `9` : Autre). | `-1` : Non renseigné. |
| **`atm`** | `int` | Conditions atmosphériques (`1` : Normale, `2` : Pluie légère, `3` : Pluie forte, `4` : Neige/grêle, `5` : Brouillard/fumée, `6` : Vent fort/tempête, `7` : Temps éblouissant, `8` : Temps couvert, `9` : Autre). | `-1` : Non renseigné. |
| **`col`** | `int` | Type de collision (`1` : Deux véhicules - frontale, `2` : Par l'arrière, `3` : Par le côté, `4` : Trois véhicules et plus - en chaîne, `5` : Collisions multiples, `6` : Autre collision, `7` : Sans collision). | `-1` : Non renseigné. |
| **`adr`** | `str` | Adresse postale (pour les accidents en agglomération). | Texte libre nettoyé des espaces superflus. |
| **`lat`** | `float` | Latitude géographique (WGS84). | Conversion des virgules en points décimaux. |
| **`long`** | `float` | Longitude géographique (WGS84). | Conversion des virgules en points décimaux. |
| **`date_accident`** | `date` | Date complète de l'accident (`AAAA-MM-JJ`). | **Colonne calculée (`propre_v2`)** à partir de `an`, `mois`, `jour`. |
| **`heure_accident`** | `time` | Heure structurée de l'accident (`HH:MM:SS`). | **Colonne calculée (`propre_v2`)** à partir de `hrmn`. |
| **`datetime_accident`** | `datetime` | Horodatage complet combinant date et heure. | **Colonne calculée (`propre_v2`)** à partir de `date_accident` et `heure_accident`. |
| **`metropole`** | `bool` | Indicateur d'appartenance à la France métropolitaine (`True` / `False`). | **Colonne calculée (`propre_v2`)** déduite du code département `dep`. |
| **`coordonnees_suspectes`** | `bool` | Indicateur d'anomalie sur les coordonnées GPS (`True` / `False`). | **Colonne calculée (`propre_v2`)** : détecte les coordonnées `(0,0)` et celles hors limites physiques, **sans vérification croisée avec le département**. |

---

## 2. Table `lieux`

| Variable | Type | Description & Modalités | Règles de nettoyage & Notes (`propre_v2`) |
| :--- | :--- | :--- | :--- |
| **`num_acc`** | `str` | Identifiant unique de l'accident. | Clé de jointure avec `caracteristiques`. |
| **`catr`** | `int` | Catégorie de route (`1` : Autoroute, `2` : Route nationale, `3` : Route départementale, `4` : Voie communale, `5` : Hors réseau public, `6` : Parc de stationnement, `7` : Routes de métropole urbaine, `9` : Autre). | `-1` : Non renseigné. |
| **`voie`** | `str` | Numéro de la route. | Chaîne nettoyée. |
| **`v1`** | `int` | Indice numérique du numéro de route (ex. `2` bis, `3` ter). | `-1` ou `NA` si non applicable. |
| **`v2`** | `str` | Lettre indice alphanumérique de la route (ex. `A`, `B`). | **Règle R004** : marqueurs invalides convertis en `pd.NA`. |
| **`circ`** | `int` | Régime de circulation (`1` : À sens unique, `2` : Bidirectionnelle, `3` : À chaussées séparées, `4` : Avec voies d'affectation variable). | `-1` : Non renseigné. |
| **`nbv`** | `int` | Nombre total de voies de circulation. | `-1` : Non renseigné. |
| **`vosp`** | `int` | Existence d'une voie réservée (`0` : Sans objet, `1` : Piste cyclable, `2` : Bande cyclable, `3` : Voie réservée). | `-1` : Non renseigné. |
| **`prof`** | `int` | Profil en long de la route (`1` : Plat, `2` : Pente, `3` : Sommet de côte, `4` : Bas de côte). | `-1` : Non renseigné. |
| **`pr`** | `int` | Numéro du PR de rattachement (borne amont). | Nettoyage des mentions parasites `"(1)"` présentes dans les fichiers bruts. |
| **`pr1`** | `int` | Distance en mètres au PR (par rapport à la borne amont). | Nettoyage des mentions parasites `"(1)"` présentes dans les fichiers bruts. |
| **`plan`** | `int` | Tracé en plan (`1` : Partie rectiligne, `2` : En courbe à gauche, `3` : En courbe à droite, `4` : En « S »). | `-1` : Non renseigné. |
| **`lartpc`** | `float` | Largeur du terre-plein central (en mètres). | **Règle R005** : valeurs conservées après typage numérique. |
| **`larrout`** | `float` | Largeur de la chaussée affectée à la circulation des véhicules (en mètres). | **Règle R003** : valeurs `-1` converties en `NA`. |
| **`surf`** | `int` | État de la surface (`1` : Normale, `2` : Mouillée, `3` : Flaques, `4` : Inondée, `5` : Enneigée, `6` : Boue, `7` : Verglacée, `8` : Corps gras/huile, `9` : Autre). | `-1` : Non renseigné. |
| **`infra`** | `int` | Aménagement - Infrastructure (`0` : Aucun, `1` : Souterrain/tunnel, `2` : Pont/autopont, `3` : Bretelle d'échangeur, `4` : Voie ferrée, `5` : Carrefour aménagé, `6` : Zone piétonne, `7` : Zone de péage, `8` : Chantier, `9` : Autres). | `-1` : Non renseigné. |
| **`situ`** | `int` | Situation de l'accident (`0` : Aucun, `1` : Sur chaussée, `2` : Sur bande d'arrêt d'urgence, `3` : Sur accotement, `4` : Sur trottoir, `5` : Sur piste cyclable, `6` : Sur autre voie spéciale, `8` : Autres). | `-1` : Non renseigné. |
| **`vma`** | `int` | Vitesse maximale autorisée sur le lieu et au moment de l'accident (en km/h). | `-1` : Non renseigné. |
| **`lieu_principal`** | `bool` | Flag identifiant l'enregistrement principal en cas de multiplicité des lieux pour un même accident (`True` / `False`). | **Colonne calculée (`propre_v2` / Règle R008)** : garantit une cardinalité `1:1` lors des jointures sans perte d'information. |
| **`vma_suspecte`** | `bool` | Indicateur d'anomalie sur la VMA (`True` / `False`). | **Colonne calculée (`propre_v2`)** : contrôle ciblant les valeurs `< 10` ou `> 130` km/h, **sans comparaison avec la catégorie de route**. |

---

## 3. Table `vehicules`

| Variable | Type | Description & Modalités | Règles de nettoyage & Notes (`propre_v2`) |
| :--- | :--- | :--- | :--- |
| **`num_acc`** | `str` | Identifiant unique de l'accident. | Clé de jointure avec `caracteristiques`. |
| **`id_vehicule`** | `str` | Identifiant unique du véhicule repris pour chacun des usagers occupant ce véhicule. | Clé de jointure avec `usagers`. |
| **`num_veh`** | `str` | Identifiant du véhicule repris pour chacun des usagers (ex. `A01`, `B01`). | Format alphanumérique standardisé. |
| **`senc`** | `int` | Sens de circulation (`0` : Inconnu, `1` : PK ou PR ou numéro d'adresse croissant, `2` : Décroissant, `3` : Absence de repère). | `-1` : Non renseigné. |
| **`catv`** | `int` | Catégorie du véhicule (`01` : Bicyclette, `02` : Cyclomoteur <50cm3, `07` : VL seul, `10` : VU seul, `13` à `15` : PL, `30` à `34` : Deux-roues motorisés, `37`–`38` : Bus/Car, `50`–`60` : EDP motorisé/non motorisé, `80` : VAE, `99` : Autre). | Nomenclature complète BAAC 2019–2024. |
| **`obs`** | `int` | Obstacle fixe heurté (`0` : Sans objet, `1` : Véhicule en stationnement, `2` : Arbre, `3` : Glissière métallique, `4` : Glissière béton, `6` : Bâtiment/mur/pile de pont, `8` : Poteau, `13` : Fossé/talus/paroi rocheuse, etc.). | `-1` : Non renseigné. |
| **`obsm`** | `int` | Obstacle mobile heurté (`0` : Aucun, `1` : Piéton, `2` : Véhicule, `4` : Véhicule sur rail, `5` : Animal domestique, `6` : Animal sauvage, `9` : Autre). | `-1` : Non renseigné. |
| **`choc`** | `int` | Point de choc initial (`0` : Aucun, `1` : Avant, `2` : Avant droit, `3` : Avant gauche, `4` : Arrière, `5` : Arrière droit, `6` : Arrière gauche, `7` : Côté droit, `8` : Côté gauche, `9` : Chocs multiples/tonneaux). | `-1` : Non renseigné. |
| **`manv`** | `int` | Manœuvre principale avant l'accident (`0` : Inconnue, `1` : Sans changement de direction, `2` : Même sens/même file, `13`–`14` : Déporté à gauche/droite, `15`–`16` : Tournant à gauche/droite, `17`–`18` : Dépassant, `23` : Arrêté, `24` : En stationnement, etc.). | `-1` : Non renseigné. |
| **`motor`** | `int` | Type de motorisation du véhicule (`0` : Inconnue, `1` : Hydrocarbures, `2` : Hybride électrique, `3` : Électrique, `4` : Hydrogène, `5` : Humaine, `6` : Autre). | `-1` : Non renseigné. |
| **`occutc`** | `int` | Nombre d'occupants dans le transport en commun. | **Règle R006** : distinction préservée entre `0` (véhicule TC vide) et `NA` (non applicable aux véhicules hors TC). |

---

## 4. Table `usagers`

| Variable | Type | Description & Modalités | Règles de nettoyage & Notes (`propre_v2`) |
| :--- | :--- | :--- | :--- |
| **`num_acc`** | `str` | Identifiant unique de l'accident. | Clé de jointure avec `caracteristiques`. |
| **`id_usager`** | `str` | Identifiant unique de l'usager. | Présent nativement depuis 2021, reconstruit ou harmonisé sur l'historique. |
| **`id_vehicule`** | `str` | Identifiant unique du véhicule associé à l'usager. | Clé de jointure avec `vehicules`. |
| **`num_veh`** | `str` | Identifiant alphanumérique du véhicule (ex. `A01`). | Rattaché au véhicule d'appartenance (ou véhicule heurtant pour un piéton). |
| **`place`** | `int` | Place occupée dans le véhicule au moment de l'accident (`1` : Conducteur, `2` à `9` : Passagers selon position, `10` : Piéton). | **`-1` : Non renseigné (concerne notamment les usagers en fuite)**. |
| **`catu`** | `int` | Catégorie d'usager (`1` : Conducteur, `2` : Passager, `3` : Piéton). | `-1` : Non renseigné. |
| **`grav`** | `int` | Gravité de blessure de l'usager (`1` : Indemne, `2` : Tué, `3` : Blessé hospitalisé, `4` : Blessé léger). | **`-1` : Non renseigné (concerne notamment les usagers en fuite)**. |
| **`sexe`** | `int` | Sexe de l'usager (`1` : Masculin, `2` : Féminin). | **`-1` : Non renseigné (concerne notamment les usagers en fuite)**. |
| **`an_nais`** | `int` | Année de naissance de l'usager (`AAAA`). | Valeurs aberrantes nettoyées ; la variable dérivée `age` n'est pas calculée dans `propre_v2`. |
| **`trajet`** | `int` | Motif du déplacement (`0` : Non renseigné, `1` : Domicile – travail, `2` : Domicile – école, `3` : Courses – achats, `4` : Utilisation professionnelle, `5` : Promenade – loisirs, `9` : Autre). | `-1` : Non renseigné. |
| **`secu1`** | `int` | Équipement de sécurité principal (`0` : Aucun équipement, `1` : Ceinture, `2` : Casque, `3` : Dispositif enfants, `4` : Gilet réfléchissant, `5` : Airbag, `6` : Gants, `7` : Gants + Airbag, `8` : Non déterminable, `9` : Autre). | `-1` : Non renseigné. |
| **`secu2`** | `int` | Second équipement de sécurité (mêmes modalités que `secu1`). | `-1` : Non renseigné. |
| **`secu3`** | `int` | Troisième équipement de sécurité (mêmes modalités que `secu1`). | `-1` : Non renseigné. |
| **`locp`** | `int` | Localisation du piéton (`0` : Sans objet, `1`–`2` : Sur chaussée, `3`–`4` : Sur passage piéton, `5` : Sur trottoir, `6` : Sur accotement, `7` : Sur refuge/BAU, `8` : Sur contre-allée, `9` : Inconnue). | `-1` : Non renseigné. |
| **`actp`** | `str` | Action du piéton (`0` : Non renseigné ou sans objet, `1` : Se déplaçant sens véhicule heurtant, `2` : Sens inverse, `3` : Traversant, `4` : Masqué, `5` : Jouant/courant, `6` : Avec animal, `9` : Autre, `A` : Monte/descend du véhicule, `B` : Inconnue). | **Arbitrage validé avec Febbe** : la valeur `0` (*Non renseigné ou sans objet* pour les non-piétons) est **conservée** telle quelle. |
| **`etatp`** | `int` | Indique si le piéton accidenté était seul ou non (`1` : Seul, `2` : Accompagné, `3` : En groupe). | `-1` : Non renseigné ou non-piéton. |
| **`doublon_suspect`** | `bool` | Flag identifiant les lignes appartenant aux groupes de doublons ambigus 2019–2020 (`True` / `False`). | **Colonne calculée (`propre_v2` / Règle R007)** : marque les 299 lignes suspectes sans suppression d'enregistrements. |