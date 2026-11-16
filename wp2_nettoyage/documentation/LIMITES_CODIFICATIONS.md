# Codifications BAAC 2019-2024 : décisions provisoires et limites

Référentiel : `wp2_nettoyage/metadata/nettoyage/codes_manquants.csv` (52 règles).
Source principale : notice ONISR « Description des bases de données annuelles 2005-2024 » (21 octobre 2025).
Responsable : Febbe Kiazi Tsaka Ngoma (WP2).

## Comment lire le référentiel
- `action = NA` : le code veut dire « non renseigné » ou « inconnu » ; la case devient vide dans `propre_v2`.
- `action = CONSERVER` : le code est une vraie information (« aucun », « sans objet ») ou une modalité non confirmée ; la valeur est gardée.
- `statut = valide_notice` : sens écrit dans la notice ONISR (la page est dans `source`).
- `statut = valide_reunion` : décidé en réunion WP2 (la notice ne définit pas -1 pour cette variable).
- `statut = a_valider` ou `a_confirmer_historique` : décision provisoire, **non appliquée** par le pipeline (seules les règles dont le statut commence par « valide » sont appliquées). La valeur d'origine reste donc dans `propre_v2`. Voir ci-dessous.

## Les 3 points encore à confirmer

| Code | Décision provisoire | Limite | Consigne pour les autres WP |
|---|---|---|---|
| `lieux.v1 = -1` | Proposé en NA, mais **pas encore appliqué** : la valeur -1 reste dans `propre_v2` | Notice muette ; 61 239 lignes (2020-2024) ; en 2019 l'absence est une case vide | Considérer v1 = -1 comme code de sens non confirmé, probablement « non renseigné » ; variable secondaire (indice bis/ter de la route), ne pas l'utiliser en analyse |
| `lieux.nbv = 0` | CONSERVER et signaler | Notice muette ; « 0 voie » est incohérent ; 9 736 lignes (2019-2024) | Exclure nbv = 0 des calculs sur le nombre de voies, ou le traiter comme inconnu |
| `usagers.actp = 7 / 8` | CONSERVER, libellé historique non officiel (« quitte / accède à l'arrêt du transport collectif ») | Absents des notices 2018, 2020 et 2025 ; libellé trouvé seulement dans le guide BAAC 2017 ; 107 et 75 lignes (2019-2024) | Conserver 7 et 8 distincts de 9 (Autre). Un regroupement analytique éventuel doit être explicite et documenté ; ne pas présenter les libellés historiques comme officiels |

## Autres points à connaître
- `pr` / `pr1` : « non renseigné » est écrit `(1)` en 2019-2022 et `-1` en 2023-2024. Les deux doivent devenir NA.
- `grav`, `sexe`, `place` = -1 : usagers en fuite ajoutés depuis 2021 (notice p. 1). Leur gravité ou leur sexe peut manquer.
- `actp = 0` : presque toujours des conducteurs et des passagers (= sans objet). Seuls 602 piétons sont concernés (2019-2022).
- `secu3 = 0` : de 200 à 800 lignes par an jusqu'en 2023, puis 10 516 en 2024. La façon de remplir a probablement changé : prudence pour comparer 2024 aux autres années.
- `catv` : aucune signification n'a changé entre 2019 et 2024. La notice écrit `00, 01…`, les fichiers écrivent `0, 1…` (même code).
