"""WP2 - Lieu principal de chaque accident (regle R008).

Depuis 2023, un accident peut avoir plusieurs lignes dans la table lieux
(31 515 accidents concernes). Toutes les lignes sont conservees, et la colonne
booleenne lieu_principal designe exactement UNE ligne par num_acc.

Le WP3 filtre lieu_principal == True pour joindre lieux aux autres tables
sans doubles comptages.

Regle de selection, deterministe et independante de l'ordre de chargement :
1. la ligne qui contient le plus d'informations exploitables
   (nombre de valeurs non manquantes dans COLONNES_INFO, apres e120) ;
2. a egalite, la route de categorie la plus importante (catr le plus petit :
   1 = autoroute, 2 = route nationale...) ;
3. a egalite, une cle construite a partir du contenu complet de la ligne,
   triee par ordre alphabetique. Deux lignes qui ont la meme cle sont
   strictement identiques : choisir l'une ou l'autre ne change rien.

A placer apres e120_valeurs_manquantes : les codes -1 doivent deja etre NA
pour ne pas etre comptes comme des informations.
"""
import pandas as pd

COLONNES_INFO = [
    "catr", "voie", "v1", "v2", "circ", "nbv", "pr", "pr1", "vosp",
    "prof", "plan", "lartpc", "larrout", "surf", "infra", "situ", "vma",
]


def appliquer(t: dict) -> dict:
    t = dict(t)
    lieux = t["lieux"].copy()

    if "lieu_principal" in lieux.columns:
        lieux = lieux.drop(columns="lieu_principal")

    colonnes_info = [c for c in COLONNES_INFO if c in lieux.columns]

    tri = pd.DataFrame(index=lieux.index)
    tri["num_acc"] = lieux["num_acc"].astype("string")
    tri["score"] = lieux[colonnes_info].notna().sum(axis=1)
    tri["catr"] = (
        pd.to_numeric(lieux["catr"].astype("string"), errors="coerce").fillna(99)
        if "catr" in lieux.columns else 99
    )
    texte = lieux.astype("string").fillna("<NA>")
    cle = texte.iloc[:, 0]
    for colonne in texte.columns[1:]:
        cle = cle + "|" + texte[colonne]
    tri["cle"] = cle

    ordre = tri.sort_values(
        ["num_acc", "score", "catr", "cle"],
        ascending=[True, False, True, True],
        kind="mergesort",
    )
    principaux = ordre.drop_duplicates("num_acc", keep="first").index

    lieux["lieu_principal"] = lieux.index.isin(principaux)
    t["lieux"] = lieux
    return t
