# Contrat d'interface WP2 vers WP3

**Version :** 0.4
**Date :** 14/11/2026
**Statut :** Validé par WP3

## 1. Objet

Definir les donnees, formats, cles et limites transmis
par WP2 a WP3 pour integration dans la zone decisionnelle.

## 2. Interface de livraison

WP2 fournit la fonction Python :

```python
from wp2_nettoyage.pipeline import donnees_propres
tables = donnees_propres()
```

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
et usagers. La jointure sur num_acc seul peut multiplier les lignes.

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
- Ne pas attribuer automatiquement à actp=7/8 la modalité 9 (« Autre »). 
- pr/pr1 = "(1)" (2019–2022) est normalisé puis traité comme valeur manquante conformément au référentiel.
- Les données -1/0 ne sont pas systématiquement converties : le sens et le traitement dépendent de la variable et de l'année.

## 8. Documentation associee

- README.md du WP2.
- metadata/nettoyage/registre_regles.csv.
- metadata/nettoyage/codes_manquants.csv.
- wp2_nettoyage/metadata/codifications/dictionnaire_baac_complet.csv.
- wp2_nettoyage/metadata/codifications/modalites_baac_finalisees.csv.
- Tests automatises et rapports de qualite.


---

## 9. Avenant propre_v3

**Version proposee :** 0.5
**Statut :** En attente de validation WP3.
**Reference :** PR #14.

Cet avenant complete le contrat v0.4 valide par WP3.
Les mentions relatives aux codes non confirmes dans `propre_v2`
decrivent la situation historique et sont remplacees par les
decisions ci-dessous pour `propre_v3`.

### 9.1 Compatibilite structurelle

Comparaison du pipeline `propre-v2` et de la branche
`fix/wp2-propre-v3` sur les donnees BAAC 2019-2024 :

| Table | Lignes V2 = V3 | Colonnes V2 = V3 |
|---|---:|---:|
| caracteristiques | 327 628 | 21 |
| lieux | 359 512 | 21 |
| vehicules | 559 847 | 12 |
| usagers | 745 158 | 18 |

Resultats :
- Aucune colonne ajoutee ou supprimee.
- Aucun type pandas modifie.
- Aucun nombre de lignes modifie.
- Total conserve : 1 992 145 lignes.
- Les valeurs corrigees evoluent volontairement entre les versions.

### 9.2 Corrections de donnees

| Variable | Correction propre_v3 | Volume |
|---|---|---:|
| caracteristiques.dep | Normalisation des departements sur un chiffre | 2 966 accidents reclasses |
| usagers.doublon_suspect | Comparaison sans id_usager | 1 280 lignes signalees, soit 981 supplementaires |
| lieux.vma | 300/500/700/900 deviennent 30/50/70/90 | 82 |
| lieux.v1 | -1 devient NA | 61 239 |
| lieux.nbv | 0 devient NA | 9 736 |
| usagers.actp | B devient NA | 1 970 |
| usagers.an_nais | 1900, age > 105 ans ou age negatif deviennent NA | 205 |

Les 82 VMA corrigees conservent `vma_suspecte=True`.
Aucune ligne n'est supprimee.

### 9.3 Consignes pour WP3

- Recharger l'entrepot a partir de `propre-v3` apres publication officielle.
- Ne pas conserver les anciennes valeurs des champs corriges.
- Conserver les usagers signales comme doublons ; aucune suppression
  automatique n'a ete effectuee.
- Ne pas considerer `nbv=0` comme une route sans voie.
- Conserver les modalites `actp=7` et `actp=8`.
- Tenir compte des 4 009 vehicules sans usager associe lors des jointures.
- Ne pas comparer directement `secu3=0` en 2024 aux annees precedentes
  sans analyser la rupture de serie.

### 9.4 Validation

Le pipeline a passe 42 tests automatises.

La compatibilite structurelle a ete verifiee par comparaison
des colonnes, types pandas et nombres de lignes des quatre tables.

Cet avenant reste soumis a validation WP3 avant d'etre considere
comme une nouvelle version du contrat approuve.
