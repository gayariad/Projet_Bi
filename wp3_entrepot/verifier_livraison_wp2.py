"""Contrôle d'acceptation d'une livraison du WP2 (tâche WP3-06).

Vérifie que donnees_propres() livre bien ce que prévoit le contrat WP2 -> WP3,
avant de construire l'entrepôt. Ne modifie rien : ni la base, ni les données.

    python -m wp3_entrepot.verifier_livraison_wp2
    python -m wp3_entrepot.verifier_livraison_wp2 --rafraichir    # relire la base au lieu du cache

Les volumes attendus (lignes et colonnes par table) sont lus dans
wp3_entrepot/reference/livraison_wp2.json : on met ce fichier à jour quand le WP2
annonce une nouvelle version, sans toucher au code.

Code de sortie : 0 si tous les contrôles bloquants passent, 1 sinon.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

REFERENCE = Path(__file__).resolve().parent / "reference" / "livraison_wp2.json"

# Colonnes qui doivent exister et n'être jamais vides (clés et dates).
NON_VIDES = {
    "caracteristiques": ["num_acc", "date_accident", "datetime_accident"],
    "lieux": ["num_acc"],
    "vehicules": ["num_acc", "id_vehicule"],
    "usagers": ["num_acc", "id_vehicule"],
}

# Les 5 indicateurs ajoutés par le WP2 : booléens, sans valeur vide.
INDICATEURS = {
    "caracteristiques": ["metropole", "coordonnees_suspectes"],
    "lieux": ["lieu_principal", "vma_suspecte"],
    "usagers": ["doublon_suspect"],
}

# Identifiants et codes géographiques : doivent rester du texte (zéros en tête, 2A/2B).
TEXTE = {
    "caracteristiques": ["num_acc", "dep", "com"],
    "lieux": ["num_acc"],
    "vehicules": ["num_acc", "id_vehicule", "num_veh"],
    "usagers": ["num_acc", "id_vehicule", "num_veh", "id_usager"],
}

GRAVITES = {1: "indemne", 2: "tué", 3: "blessé hospitalisé", 4: "blessé léger"}
CATU_PIETON = 3


def nb(n):
    """1234567 -> '1 234 567'."""
    return f"{n:,}".replace(",", " ")


def charger_reference(chemin=REFERENCE):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def _texte(serie):
    return serie.astype("string")


def _cle_vehicule(df):
    return _texte(df["num_acc"]) + "|" + _texte(df["id_vehicule"])


def copies_doublon(usagers):
    """Vrai pour les copies en plus de la première dans un groupe doublon_suspect.

    Même comparaison que l'étape e140 du WP2 (toutes les colonnes sauf id_usager
    et doublon_suspect) : c'est le futur champ copie_doublon de l'entrepôt.
    """
    colonnes = [c for c in usagers.columns if c not in {"id_usager", "doublon_suspect"}]
    suspect = usagers["doublon_suspect"].eq(True).fillna(False).astype(bool)
    return suspect & usagers.duplicated(subset=colonnes, keep="first")


def verifier(t, reference):
    """Renvoie une liste de (statut, message) ; statut vaut OK, ECHEC ou INFO."""
    res = []
    lignes_attendues = reference["lignes"]
    colonnes_attendues = reference["colonnes"]

    def controle(ok, message):
        res.append(("OK" if ok else "ECHEC", message))

    def info(message):
        res.append(("INFO", message))

    # 1. Les 4 tables sont là
    manquantes = sorted(set(lignes_attendues) - set(t))
    detail = f" : manquantes {manquantes}" if manquantes else ""
    controle(not manquantes, "4 tables livrées" + detail)
    if manquantes:
        return res

    # 2. Nombre de lignes et de colonnes, lus dans le fichier de référence
    for nom, attendu in lignes_attendues.items():
        n = len(t[nom])
        controle(n == attendu, f"{nom} : {nb(n)} lignes (attendu {nb(attendu)})")
    for nom, attendu in colonnes_attendues.items():
        n = t[nom].shape[1]
        controle(n == attendu, f"{nom} : {n} colonnes (attendu {attendu})")

    # 3. Colonnes obligatoires présentes et remplies
    for nom, colonnes in NON_VIDES.items():
        df = t[nom]
        absentes = [c for c in colonnes if c not in df.columns]
        vides = {c: int(df[c].isna().sum()) for c in colonnes if c in df.columns}
        vides = {c: n for c, n in vides.items() if n}
        detail = []
        if absentes:
            detail.append(f"absentes {absentes}")
        if vides:
            detail.append(f"vides {vides}")
        suite = " -> " + ", ".join(detail) if detail else " présentes et remplies"
        controle(not detail, f"{nom} : colonnes obligatoires {colonnes}{suite}")

    # 4. Les 5 indicateurs booléens du WP2
    for nom, colonnes in INDICATEURS.items():
        df = t[nom]
        for c in colonnes:
            if c not in df.columns:
                controle(False, f"{nom}.{c} : absent")
                continue
            serie = df[c]
            ok = pd.api.types.is_bool_dtype(serie) and not serie.isna().any()
            controle(ok, f"{nom}.{c} : booléen sans vide (type {serie.dtype})")

    # 5. Identifiants restés en texte
    for nom, colonnes in TEXTE.items():
        df = t[nom]
        for c in colonnes:
            if c not in df.columns:
                controle(False, f"{nom}.{c} : absente")
                continue
            ok = not pd.api.types.is_numeric_dtype(df[c])
            controle(ok, f"{nom}.{c} : texte (type {df[c].dtype})")

    car, lieux, veh, usa = (t[n] for n in ("caracteristiques", "lieux", "vehicules", "usagers"))

    # 6. Unicité des clés
    doublons_acc = int(car["num_acc"].duplicated().sum())
    controle(doublons_acc == 0, f"caracteristiques.num_acc unique ({doublons_acc} doublon(s))")
    doublons_veh = int(veh.duplicated(["num_acc", "id_vehicule"]).sum())
    controle(
        doublons_veh == 0, f"vehicules (num_acc, id_vehicule) unique ({doublons_veh} doublon(s))"
    )

    # 7. Exactement un lieu principal par accident
    if "lieu_principal" in lieux.columns:
        masque = lieux["lieu_principal"].eq(True).fillna(False).astype(bool)
        par_acc = _texte(lieux.loc[masque, "num_acc"]).value_counts()
        plusieurs = int((par_acc > 1).sum())
        sans = int((~_texte(car["num_acc"]).isin(par_acc.index)).sum())
        controle(
            plusieurs == 0 and sans == 0,
            f"lieux.lieu_principal : 1 par accident ({nb(int(masque.sum()))} lignes, "
            f"{sans} accident(s) sans, {plusieurs} avec plusieurs)",
        )

    # 8. Aucune ligne orpheline
    ids_acc = _texte(car["num_acc"])
    for nom, df in (("lieux", lieux), ("vehicules", veh), ("usagers", usa)):
        orphelins = int((~_texte(df["num_acc"]).isin(ids_acc)).sum())
        controle(orphelins == 0, f"{nom} -> caracteristiques : {orphelins} ligne(s) orpheline(s)")
    orphelins = int((~_cle_vehicule(usa).isin(_cle_vehicule(veh))).sum())
    controle(orphelins == 0, f"usagers -> vehicules : {orphelins} ligne(s) orpheline(s)")

    # 9. Gravité : codes connus ou vide
    if "grav" in usa.columns:
        grav = pd.to_numeric(_texte(usa["grav"]), errors="coerce")
        inconnus = int((usa["grav"].notna() & ~grav.isin(list(GRAVITES))).sum())
        controle(
            inconnus == 0, f"usagers.grav : codes 1 à 4 ou vide ({inconnus} code(s) inconnu(s))"
        )
        repartition = ", ".join(
            f"{code}={GRAVITES[code]} : {nb(int((grav == code).sum()))}" for code in GRAVITES
        )
        info(f"usagers.grav : {repartition}")
        info(f"usagers.grav vide : {int(grav.isna().sum())}")
    else:
        controle(False, "usagers.grav : absente")

    # 10. Informations, sans blocage
    info(
        f"fait_usager aura {nb(len(usa))} lignes pour {nb(len(car))} accidents : "
        "compter les accidents avec COUNT(DISTINCT num_acc)"
    )
    if "doublon_suspect" in usa.columns:
        suspects = int(usa["doublon_suspect"].eq(True).sum())
        copies = int(copies_doublon(usa).sum())
        info(
            f"usagers : {nb(suspects)} ligne(s) doublon_suspect, dont {nb(copies)} copie(s) "
            "en trop (futur copie_doublon) ; filtrer doublon_suspect retirerait aussi "
            f"{nb(suspects - copies)} ligne(s) d'origine"
        )
    if "catu" in usa.columns:
        catu = pd.to_numeric(_texte(usa["catu"]), errors="coerce")
        pietons = catu == CATU_PIETON
        sans_vehicule = int((pietons & usa["id_vehicule"].isna()).sum())
        info(
            f"usagers piétons (catu=3) : {nb(int(pietons.sum()))}, dont {sans_vehicule} sans id_vehicule"
        )
    sans_usager = int((~_cle_vehicule(veh).isin(_cle_vehicule(usa))).sum())
    info(f"vehicules sans usager associé : {nb(sans_usager)} (absents de fait_usager)")
    if "coordonnees_suspectes" in car.columns:
        info(
            f"caracteristiques.coordonnees_suspectes : {int(car['coordonnees_suspectes'].eq(True).sum())}"
        )
    if "metropole" in car.columns:
        info(f"caracteristiques hors métropole : {nb(int(car['metropole'].eq(False).sum()))}")
    if "vma_suspecte" in lieux.columns:
        info(f"lieux.vma_suspecte : {int(lieux['vma_suspecte'].eq(True).sum())}")
    for c in ("dep", "com"):
        if c in car.columns:
            info(f"caracteristiques.{c} vide : {int(car[c].isna().sum())}")

    return res


def version_git():
    try:
        return subprocess.run(
            ["git", "describe", "--tags", "--always", "--dirty"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "inconnue"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rafraichir", action="store_true", help="relire la base au lieu du cache")
    args = parser.parse_args()

    from wp2_nettoyage.pipeline import donnees_propres

    reference = charger_reference()
    print(f"Version du dépôt : {version_git()}")
    print(f"Référence : {reference['version_wp2']} ({REFERENCE.name})")
    print("Chargement de donnees_propres()...")
    t = donnees_propres(rafraichir=args.rafraichir)

    res = verifier(t, reference)
    for statut, message in res:
        print(f"[{statut:<5}] {message}")

    echecs = sum(statut == "ECHEC" for statut, _ in res)
    controles = sum(statut != "INFO" for statut, _ in res)
    print()
    if echecs:
        print(f"LIVRAISON REFUSÉE : {echecs} contrôle(s) bloquant(s) en échec sur {controles}.")
    else:
        print(f"LIVRAISON ACCEPTÉE : {controles} contrôles bloquants réussis.")
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
