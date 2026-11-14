# Contrat d'interface WP2 vers WP3

**Version :** 0.4
**Date :** 14/11/2026
**Statut :** Validé par WP3

## 1. Objet

Definir les donnees, formats, cles et limites transmis
par WP2 a WP3 pour integration dans la zone decisionnelle.

## 2. Interface de livraison

WP2 fournit la fonction Python :

`from wp2_nettoyage.pipeline import donnees_propres`
`tables = donnees_propres()`

Elle retourne quatre DataFrames pandas :

| Table | Grain | Lignes |
|---|---|---:|
| caracteristiques | Accident | 327 628 |
| lieux | Enregistrement de lieu | 359 512 |
| vehicules | Vehicule | 559 847 |
| usagers | Enregistrement d'usager | 745 158 |

## 3. Formats et types

- Donnees BAAC 2019-2024.
- Identifiant accident : num_acc.
- Typage pandas applique par e115_typage.
- Dates et heures construites dans caracteristiques.
- Valeurs absentes normalisees en pd.NA.
- Aucun export CSV final n'est impose par ce contrat.

## 4. Cles et cardinalites

### Caracteristiques vers vehicules

- Cle accident : num_acc.
- Relation observee : un accident vers plusieurs vehicules.
- Cle unique des vehicules : (num_acc, id_vehicule).

### Caracteristiques vers usagers

- Cle accident : num_acc.
- Plusieurs usagers peuvent appartenir au meme accident.
- id_usager n'est pas disponible dans les sources 2019-2020.

### Caracteristiques vers lieux

- Cle accident : num_acc.
- Les donnees 2023 et 2024 peuvent contenir
  plusieurs lignes de lieux pour un accident.
- Ne pas imposer de contrainte UNIQUE sur lieux.num_acc.
- lieu_principal=True identifie une ligne de référence par accident lorsque l'analyse exige un seul lieu

### Vehicules vers usagers

- Jointure recommandee :
  vehicules.num_acc = usagers.num_acc
  ET vehicules.id_vehicule = usagers.id_vehicule.

## 5. Regles de jointure

Attention : joindre simultanement lieux, vehicules
et usagers sur num_acc seul peut multiplier les lignes.

Pour calculer le nombre d'accidents :
COUNT(DISTINCT num_acc), au bon niveau de granularite.

Pour les statistiques usagers :
travailler au niveau des enregistrements usagers,
avec une politique explicite sur les doublons 2019-2020.

Pour les statistiques vehicules :
utiliser la cle composite accident-vehicule.

La strategie de modelisation finale revient a WP3.

## 6. Transformations appliquees

Le pipeline applique dans cet ordre :

e100, e110, e115, e120, e125, e130, e140, e150.

- Harmonisation, typage, dates et heures.
- Traitement des valeurs manquantes selon les regles ONISR validees.
- Signalement des valeurs hors plage, sans suppression.
- caracteristiques.metropole : permet un filtre métropole sans supprimer les observations d'outre-mer.
- caracteristiques.coordonnees_suspectes : détecte les coordonnées (0,0) et les latitudes/longitudes hors limites physiques mondiales, sans contrôler l'appartenance aux frontières françaises.
- lieux.vma_suspecte : controle de vitesse, seuil 10-130.
- lieux.lieu_principal : exactement un lieu principal par accident.
- usagers.doublon_suspect : signalement sans suppression.

## 7. Restrictions et limites

- Les 1 992 145 lignes sont conservees.
- Les doublons d'usagers historiques restent presents.
- Les lignes multiples de lieux sont conservees.
- R006 est validee : occutc est conservee sans imputation automatique.
- L'interpretation de occutc selon catv doit etre prise en compte par WP3.
- Le seuil VMA reste un critere provisoire de signalement.
- La qualite metier exhaustive n'est pas garantie.
- lartpc a une incomplétude d'environ 99,84 % et nécessite des précautions pour les indicateurs.
- Les règles de statut valide_notice ou valide_reunion autorisent la conversion en NA lorsqu'elle est prévue.
- Les codes non confirmés restent inchangés dans propre_v2 : v1=-1, nbv=0, actp=7/8.
- Ne pas attribuer automatiquement à actp=7/8 la modalité 9 (« Autre »). pr/pr1 = "(1)" (2019–2022) est normalisé puis traité comme valeur manquante conformément au référentiel.
-  Les données -1/0 ne sont pas systématiquement converties : le sens et le traitement dépendent de la variable et de l'année.

## 8. Documentation associee

- README.md du WP2.
- metadata/nettoyage/registre_regles.csv.
- metadata/nettoyage/codes_manquants.csv.
- wp2_nettoyage/metadata/codifications/dictionnaire_baac_complet.csv.
- wp2_nettoyage/metadata/codifications/modalites_baac_finalisees.csv.
- Tests automatises et rapports de qualite.
