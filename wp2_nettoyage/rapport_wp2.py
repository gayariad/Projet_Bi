"""Rapport d'acceptation technique WP2 / propre_v2 (exécution depuis la racine du dépôt).

Ce script vérifie le pipeline et la conservation des volumes ; les nombres de
référence dépendent du périmètre BAAC 2019–2024 utilisé lors de la recette.
"""
import pandas as pd
from commun.recuperer_donnees import charger_tout
from wp2_nettoyage.pipeline import donnees_propres

ATTENDUS = {"caracteristiques": 327628, "lieux": 359512, "vehicules": 559847, "usagers": 745158}
brut = charger_tout()
propre = donnees_propres()

print("=== VOLUMETRIE BRUT / PROPRE ===")
for famille, attendu in ATTENDUS.items():
    n_brut, n_propre = len(brut[famille]), len(propre[famille])
    assert n_brut == n_propre == attendu, f"{famille}: brut {n_brut}, propre {n_propre}, attendu {attendu}"
    print(f"{famille}: {n_brut} -> {n_propre} (0 suppression)")
assert sum(len(t) for t in propre.values()) == 1992145

c, l, v, u = (propre[n] for n in ("caracteristiques", "lieux", "vehicules", "usagers"))

print("\n=== R008 : UN LIEU PRINCIPAL PAR ACCIDENT ===")
assert "lieu_principal" in l and "num_acc" in l
assert not l["num_acc"].isna().any()
per_acc = l.groupby("num_acc", dropna=False)["lieu_principal"].sum()
assert per_acc.eq(1).all(), "R008 : un accident n'a pas exactement un lieu principal"
assert set(l["num_acc"]) == set(c["num_acc"]), "R008 : périmètre accidents incohérent"
print(f"OK : {len(per_acc)} accidents avec exactement un lieu principal")

print("\n=== R007 : DOUBLONS CONSERVES ET SIGNALES ===")
assert "doublon_suspect" in u
attendus_doublons = u.drop(columns=["doublon_suspect"]).duplicated(keep=False)
assert u["doublon_suspect"].fillna(False).eq(attendus_doublons).all()
print(f"OK : {int(u['doublon_suspect'].sum())} lignes signalées (référence historique : 299)")
assert int(u["doublon_suspect"].sum()) == 299

print("\n=== METROPOLE ===")
assert "metropole" in c and c["metropole"].dtype == bool
assert int(c["metropole"].sum()) == 306790
print("OK : 306790 accidents métropolitains")

print("\n=== E125 : INDICATEURS DE CONTROLE ===")
assert "coordonnees_suspectes" in c and "vma_suspecte" in l
lat = pd.to_numeric(c["lat"], errors="coerce")
lon = pd.to_numeric(c["long"], errors="coerce")
expected_coords = (((lat == 0) & (lon == 0)) | (lat.notna() & ~lat.between(-90, 90)) | (lon.notna() & ~lon.between(-180, 180))).fillna(False)
assert c["coordonnees_suspectes"].eq(expected_coords).all()
vma = pd.to_numeric(l["vma"], errors="coerce")
expected_vma = ((vma < 10) | (vma > 130)).fillna(False)
assert l["vma_suspecte"].eq(expected_vma).all()
print(f"OK : {int(c['coordonnees_suspectes'].sum())} coordonnées suspectes, {int(l['vma_suspecte'].sum())} VMA suspectes ; lignes conservées")
print("Attention : limites physiques mondiales et seuil VMA provisoire, pas un contrôle France exhaustif")

print("\n=== TYPES ATTENDUS (E115) ===")
from wp2_nettoyage.etapes.e115_typage import ENTIERS, DECIMAUX
for famille, colonnes in ENTIERS.items():
    for col in colonnes:
        assert pd.api.types.is_integer_dtype(propre[famille][col]), f"{famille}.{col} non entier"
for famille, colonnes in DECIMAUX.items():
    for col in colonnes:
        assert pd.api.types.is_float_dtype(propre[famille][col]), f"{famille}.{col} non décimal"
for col in ("date_accident", "datetime_accident"):
    assert pd.api.types.is_datetime64_any_dtype(c[col]), f"{col} non datetime"
print("OK : types attendus e115 cohérents")

print("\n=== R006 : PRESERVATION D'OCCUTC ===")
assert "occutc" in v
# Ne pas déduire automatiquement sans objet vs manquant à partir du NA seul.
print("OK : occutc présente ; interprétation métier selon catv explicitée dans le contrat")
print("\nCONCLUSION : CONTROLES TECHNIQUES PASSÉS ; validation WP3 et règles métier documentaires distinctes")
