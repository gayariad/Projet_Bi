# Réponse du WP3 au contrat d'interface WP2 vers WP3

**Version :** 0.3 (validée par le WP3 le 23/11/2026, en attente du WP2)
**Date :** 23/11/2026
**Rédigé par :** Mouad Sahraoui Doukkali, WP3 (tâche WP3-06)
**Répond à :** `wp2_nettoyage/documentation/contrat_interface_wp2_wp3.md` v0.4 du 14/11/2026
et son avenant propre-v3 (v0.5, section 9, en attente de validation du WP3)
**Livraisons contrôlées :** `propre-v2` (15/11/2026, 33/33) et `propre-v3` (23/11/2026, 37/37)
**Validation :** Abderrahmane (chef du WP3) le 23/11/2026 ; Mohamed Reda (chef du WP2) en attente

## En résumé

- Le WP3 accepte la livraison par `donnees_propres()`, les règles de nettoyage du WP2
  et l'avenant propre-v3, sous réserve que le contrôle de livraison passe sur le tag `propre-v3`.
- La table de faits `fait_usager` est au grain **une ligne par usager** (745 158 lignes).
  Pour compter des accidents, tous les WP utilisent `COUNT(DISTINCT num_acc)`.
- Le WP3 fait **trois demandes** au WP2 : un tag Git et une annonce à chaque version (point 9),
  un préavis de 48 h pour tout changement de structure (point 9), des identifiants et codes
  géographiques qui restent en texte (point 3).
- Le WP3 prend **quatre décisions** de son côté, sans rien demander au WP2 : NULL conservé
  (point 4), lieu principal seul (point 5), champ `copie_doublon` (point 6), clé `fait_usager_id` (point 7).
- Trois questions restent ouvertes, avec destinataire et date limite : voir « Questions ouvertes ».

## Résultat du contrôle de livraison

Commande : `python -m wp3_entrepot.verifier_livraison_wp2`. Les volumes attendus sont lus dans
`wp3_entrepot/reference/livraison_wp2.json`.

| Mesure | propre-v2 (15/11) | propre-v3 (23/11) |
|---|---:|---:|
| Contrôles bloquants réussis | 33 / 33 | 37 / 37 (ajout du nombre de colonnes) |
| Lignes : caractéristiques, lieux, véhicules, usagers | 327 628 · 359 512 · 559 847 · 745 158 | identiques |
| Usagers à gravité vide | 419 | 419 |
| Lignes `doublon_suspect` | 299 | 1 280 |
| dont copies en trop (`copie_doublon`) | 164 | 739 |
| Usagers sans `id_vehicule`, piétons compris | 0 | 0 (57 513 piétons, tous rattachés à un véhicule) |
| Accidents hors métropole | 20 838 | 17 872 |
| `vma_suspecte` | 457 | 457 |
| Véhicules sans usager associé | non mesuré | 4 009 |

La livraison propre-v3 (commit `bc137bb` de `main`, contrôle du 23/11/2026) est acceptée.
Les 419 usagers à gravité vide sont confirmés sur les deux versions.
La baisse des accidents hors métropole (20 838 puis 17 872, soit 2 966) correspond exactement
aux départements reclassés par l'avenant, et les 4 009 véhicules sans usager aussi.
Tous les usagers ont un `id_vehicule`, piétons compris : la BAAC rattache chaque piéton
au véhicule qui l'a heurté.

## Grain de la table de faits

- `fait_usager` contient **une ligne par enregistrement d'usager** de `propre`, soit 745 158 lignes
  pour 327 628 accidents (2,3 usagers par accident en moyenne).
- **Avertissement pour tous les WP :** `COUNT(*)` sur `fait_usager` compte des usagers, pas des
  accidents. Pour les accidents, utiliser `COUNT(DISTINCT num_acc)`. Sinon les indicateurs du WP4
  sont gonflés d'un facteur 2,3. La même règle figure dans `wp3_entrepot/CONVENTIONS_SQL.md`.
- Les véhicules sans usager associé (4 009 selon l'avenant, section 9.3) n'apparaissent pas dans
  `fait_usager`. Les nombres de véhicules se calculent à partir de la table des véhicules.
- Le détail des dimensions reste le livrable du modèle en étoile (WP3-03). Ce document fixe
  seulement ce que la livraison du WP2 doit permettre.

## Position du WP3, point par point

La numérotation reprend les 10 points de la v0.3 du contrat.

### 1. Séparateur et encodage : sans objet

Il n'y a pas d'export CSV : le WP3 lit directement `donnees_propres()`.

### 2. Noms des colonnes : accepté, noms BAAC conservés

Les noms de `propre` sont gardés tels quels dans l'entrepôt, comme le prévoit
`wp3_entrepot/CONVENTIONS_SQL.md` (WP3-02), y compris `int`, `lat` et `long` que PostgreSQL
accepte comme noms de colonnes. La v0.1 proposait de les renommer : c'est abandonné.
Les tables suivent la convention WP3-02 : `fait_...`, `dim_...`, `ref_...`, `v_...`.

### 3. Types : accepté, colonne par colonne

Règle : toute colonne entière de `propre` (`Int64`) devient `SMALLINT`. Les valeurs les plus
grandes (`an_nais`, `vma`, `occutc`) restent très loin de la limite de 32 767.
`INTEGER` est réservé aux clés techniques du WP3 (`fait_usager_id`, clés `..._id` des dimensions)
et aux compteurs `nb_...`.

| Table | `SMALLINT` | `DOUBLE PRECISION` | `TEXT` | Autres |
|---|---|---|---|---|
| caracteristiques | `jour`, `mois`, `an`, `annee`, `lum`, `agg`, `int`, `atm`, `col` | `lat`, `long` | `num_acc`, `dep`, `com`, `hrmn`, `adr` | `date_accident` DATE, `heure_accident` TIME, `datetime_accident` TIMESTAMP, `metropole` et `coordonnees_suspectes` BOOLEAN |
| lieux | `catr`, `circ`, `nbv`, `vosp`, `prof`, `plan`, `surf`, `infra`, `situ`, `vma`, `annee` | `lartpc`, `larrout` | `num_acc`, `voie`, `v1`, `v2`, `pr`, `pr1` | `vma_suspecte` et `lieu_principal` BOOLEAN |
| vehicules | `senc`, `catv`, `obs`, `obsm`, `choc`, `manv`, `motor`, `occutc`, `annee` | | `num_acc`, `id_vehicule`, `num_veh` | |
| usagers | `place`, `catu`, `grav`, `sexe`, `an_nais`, `trajet`, `secu1`, `secu2`, `secu3`, `locp`, `etatp`, `annee` | | `num_acc`, `id_vehicule`, `num_veh`, `id_usager`, `actp` | `doublon_suspect` BOOLEAN |

**Demande au WP2 :** les identifiants (`num_acc`, `id_vehicule`, `num_veh`, `id_usager`) et les
codes géographiques (`dep`, `com`) restent en texte dans toutes les versions, pour garder les
zéros en tête et 2A / 2B. `com` sert de clé de jointure avec la population INSEE (WP3-10).

### 4. Valeurs non renseignées : accepté, NULL conservé

Le remplacement par `pd.NA` est accepté. Conformément à `CONVENTIONS_SQL.md`, l'entrepôt
garde NULL sans le remplacer. Power BI l'affiche « Non renseigné ».
La v0.1 proposait un membre « Unknown » (clé -1) : c'est abandonné.

- Les usagers à gravité vide (419) restent dans `fait_usager`. Le WP4 et les WP5 à WP7 les
  excluent explicitement de leurs taux de gravité.
- Les codes traités par l'avenant propre-v3 (`v1`, `nbv`, `actp = B`) sont repris tels que livrés.
  `nbv` vide ne signifie pas « route sans voie ».

### 5. Jointure avec `lieux` : accepté

Le WP3 ne joint que les lignes `lieu_principal = TRUE`, soit une ligne par accident (327 628).
Les lignes secondaires de 2023-2024 restent dans `propre` mais ne sont pas chargées dans la
première version de l'entrepôt.

### 6. Doublons d'usagers : conservés et signalés

Le WP3 ne supprime aucune ligne. La table de faits garde toutes les lignes, avec deux champs :

- `doublon_suspect` (WP2) : vrai pour **toutes** les lignes d'un groupe identique.
  Depuis propre-v3, la comparaison se fait sans `id_usager`.
- `copie_doublon` (WP3, hors contrat) : vrai seulement pour les copies **en plus** de la première
  ligne du groupe, avec la même comparaison que le WP2.

**Attention pour tous les WP :** pour dédoublonner, filtrer `copie_doublon = FALSE`.
Filtrer `doublon_suspect = FALSE` retire aussi les lignes d'origine : 541 lignes de trop sur propre-v3
(135 sur propre-v2).

### 7. Clé des usagers : `fait_usager_id`

- `fait_usager_id` (INTEGER) est la **clé primaire de `fait_usager`**. Si le modèle (WP3-03)
  regroupe les attributs de l'usager dans une `dim_usager` par profil (catégorie, tranche d'âge…),
  cette dimension a sa propre clé (`usager_id`, selon `CONVENTIONS_SQL.md`) ;
  `fait_usager_id` reste la clé du fait.
- La clé est attribuée après un tri sur toutes les colonnes. Elle est **stable pour une même
  livraison, pas d'une version à l'autre** : une ligne ajoutée ou retirée décale la numérotation.
  Personne ne la stocke ni ne s'y réfère en dehors de l'entrepôt.
- `id_usager` est gardé comme simple attribut, vide en 2019-2020.
- **Proposition pour le découpage train/test des WP5 à WP7 :** découper sur `num_acc` avec une
  graine fixe, pas sur `fait_usager_id`. Tous les usagers d'un même accident tombent du même côté,
  ce qui évite la fuite d'information entre usagers d'un même accident. Décision : Q3.

### 8. Colonnes obligatoires

Toutes les colonnes de `propre` sont gardées : 21 pour caractéristiques, 21 pour lieux,
12 pour véhicules, 18 pour usagers (avenant, section 9.1).
Doivent être présentes et **jamais vides** :

| Table | Colonnes |
|---|---|
| `caracteristiques` | `num_acc`, `date_accident`, `datetime_accident` |
| `lieux` | `num_acc` |
| `vehicules` | `num_acc`, `id_vehicule` |
| `usagers` | `num_acc`, `id_vehicule` (piétons compris) |

Les **5 indicateurs du WP2** doivent être présents, booléens et sans valeur vide :

| Indicateur | Table |
|---|---|
| `metropole` | caracteristiques |
| `coordonnees_suspectes` | caracteristiques |
| `vma_suspecte` | lieux |
| `lieu_principal` | lieux |
| `doublon_suspect` | usagers |

`copie_doublon` n'en fait pas partie : c'est un champ calculé par le WP3, hors contrat.
Les colonnes `dep`, `com` et `grav` doivent être présentes ; leurs valeurs vides sont
tolérées et comptées.

### 9. Dépôt et versionnement

- Chaque version est un tag Git sur `main` (`propre-v2`, `propre-v3`…), annoncé sur Discord
  avec la liste des changements.
- Changement **ajouté** (nouvelle colonne, nouvel indicateur, nouvelle règle validée) :
  libre, simplement annoncé.
- Changement **de structure** (colonne renommée, supprimée ou retypée, nombre de lignes modifié) :
  annoncé au moins 48 h avant et accepté par le WP3.
- À chaque version, le WP3 lance le contrôle de livraison puis reconstruit l'entrepôt
  (`python -m wp3_entrepot.construire`). La table `entrepot.version` garde le commit utilisé.
- Les versions du WP2 sont gelées le 11/12 (calendrier du WP0).

### 10. Règles d'acceptation d'une livraison

Le WP3 lance `python -m wp3_entrepot.verifier_livraison_wp2`. Les volumes attendus sont lus dans
`wp3_entrepot/reference/livraison_wp2.json`, mis à jour par le WP3 quand le WP2 annonce une version.
Les contrôles suivants sont **bloquants** :

1. les 4 tables sont livrées ;
2. les nombres de lignes et de colonnes sont ceux du fichier de référence ;
3. les colonnes obligatoires du point 8 sont présentes et remplies ;
4. les 5 indicateurs sont booléens et sans valeur vide ;
5. les identifiants et `dep`, `com` sont du texte ;
6. `num_acc` est unique dans `caracteristiques`, et `(num_acc, id_vehicule)` dans `vehicules` ;
7. il y a exactement une ligne `lieu_principal = TRUE` par accident ;
8. aucune ligne orpheline : `lieux`, `vehicules` et `usagers` vers `caracteristiques`,
   et `usagers` vers `vehicules` ;
9. `grav` vaut 1, 2, 3, 4 ou vide.

Sont seulement **affichés** : la répartition de la gravité, les gravités vides, les doublons et
copies en trop, les piétons sans `id_vehicule`, les véhicules sans usager, les coordonnées et
VMA suspectes, les accidents hors métropole, les `dep` et `com` vides.
La livraison est acceptée si tous les contrôles bloquants passent. Le résultat est publié
dans le salon du WP3.

## Avenant propre-v3 : position du WP3

Le WP3 accepte l'avenant v0.5, sous réserve que le contrôle passe sur le tag `propre-v3`.
Consignes de la section 9.3 et ce que le WP3 en fait :

| Consigne du WP2 | Ce que fait le WP3 |
|---|---|
| Recharger l'entrepôt à partir de `propre-v3` après publication | Contrôle de livraison, puis reconstruction complète (WP3-15) |
| Ne pas conserver les anciennes valeurs des champs corrigés | Reconstruction complète, sans mise à jour partielle |
| Conserver les usagers signalés comme doublons | Toutes les lignes gardées, avec `copie_doublon` (point 6) |
| `nbv = 0` n'est pas une route sans voie | Repris vide (NULL) et signalé dans le guide de l'entrepôt (WP3-13) |
| Conserver les modalités `actp = 7` et `actp = 8` | Gardées, avec leurs libellés dans `ref_...` (WP3-04) |
| 4 009 véhicules sans usager associé | Absents de `fait_usager` ; comptés depuis la table des véhicules |
| Rupture de série de `secu3 = 0` en 2024 | Signalée dans le guide pour le WP4 et les WP5 à WP7 |

## Questions ouvertes

| N° | Question | Destinataire | Réponse attendue le |
|---|---|---|---|
| Q1 | Sur propre-v3, 739 copies en trop contre 164 sur propre-v2. La hausse vient surtout de 2021-2024, où ces lignes ont pourtant des `id_usager` différents. Le WP2 confirme-t-il que ce sont des copies, et pas des personnes distinctes ? | WP2 (Mohamed Reda) | mer. 25/11/2026 |
| Q2 | Les identifiants et `dep`, `com` restent-ils en texte dans toutes les versions jusqu'au gel ? Quand le tag `propre-v3` sera-t-il publié ? | WP2 (Mohamed Reda) | mer. 25/11/2026 |
| Q3 | Le découpage train/test se fait-il sur `num_acc` avec une graine fixe ? | WP0 et WP5 à WP7 | jeu. 26/11/2026 |

## Points d'attention pour la suite

- `occutc` : conservé tel quel (règle R006). Il n'a de sens que pour certaines catégories de
  véhicules (`catv`) : le guide de l'entrepôt (WP3-13) le précisera.
- Seuil VMA : provisoire. Le WP3 garde `vma` et `vma_suspecte` sans les modifier.
- `lartpc` est vide à environ 99,84 % : à ne pas utiliser dans les indicateurs.

## Validation

| Rôle | Nom | Accord | Date |
|---|---|---|---|
| Chef du WP2 | Mohamed Reda | | |
| Chef du WP3 | Abderrahmane | Oui (message Discord) | 23/11/2026 |
| WP3-06 | Mouad Sahraoui Doukkali | Oui (auteur) | 23/11/2026 |

## Historique

| Version | Date | Changements |
|---|---|---|
| 0.1 | 16/11/2026 | Première proposition, réponses aux 10 points de la v0.3 |
| 0.2 | 23/11/2026 | Relecture du chef du WP3 : grain de `fait_usager`, types colonne par colonne, clé `fait_usager_id` et découpage train/test, liste des 5 indicateurs, questions ouvertes. Alignement sur `CONVENTIONS_SQL.md` (NULL conservé, noms BAAC). Position sur l'avenant propre-v3. Volumes du contrôle lus dans un fichier de référence |
| 0.3 | 23/11/2026 | Accord du chef du WP3. Précision sur `dim_usager` (point 7) |