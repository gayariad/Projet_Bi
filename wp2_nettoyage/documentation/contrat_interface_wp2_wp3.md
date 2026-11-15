# Contrat d'interface provisoire WP2 vers WP3

**Version :** 0.3
**Date :** 13/11/2026
**Statut :** PROPOSITION - non encore acceptee par WP3

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
- Les formats de stockage cibles restent a confirmer avec WP3.

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
- caracteristiques.metropole : indicateur geographique.
- caracteristiques.coordonnees_suspectes : controle geographique.
- lieux.vma_suspecte : controle de vitesse, seuil provisoire 10-130.
- lieux.lieu_principal : exactement un lieu principal par accident.
- usagers.doublon_suspect : signalement sans suppression.

## 7. Restrictions et limites

- Les 1 992 145 lignes sont conservees.
- Les doublons d'usagers historiques restent presents.
- Les lignes multiples de lieux sont conservees.
- R006 est validee : occutc est conservee sans imputation automatique.
- L'interpretation de occutc selon catv doit etre prise en compte par WP3.
- Certaines modalites ONISR restent a confirmer.
- Le seuil VMA reste un critere provisoire de signalement.
- La qualite metier exhaustive n'est pas garantie.

## 8. Documentation associee

- README.md du WP2.
- metadata/nettoyage/registre_regles.csv.
- metadata/nettoyage/codes_manquants.csv.
- Dictionnaire BAAC et codifications disponibles.
- Tests automatises et rapports de qualite.

## 9. Points a confirmer avec WP3

- [ ] Separateur et encodage acceptes.
- [ ] Noms des fichiers et des colonnes acceptes.
- [ ] Types cibles des donnees.
- [ ] Gestion des valeurs non renseignees.
- [ ] Strategie de jointure avec lieux.
- [ ] Gestion des doublons d'usagers 2019-2020.
- [ ] Strategie d'identification des usagers sans id_usager.
- [ ] Besoins sur les colonnes obligatoires.
- [ ] Methode de depot et de versionnement.
- [ ] Regles d'acceptation de la livraison.

## 10. Critere de validation de l'interface

Ce document deviendra un contrat valide lorsque
les representants WP2 et WP3 auront confirme
les points precedents et consigne leur accord.

Aucune acceptation n'est presumee a ce stade.
