#!/usr/bin/env python3
"""Vérifie qu'une PR n'ajoute pas de fichier trop lourd.

Usage : fichiers_lourds.py --max-mo 5 fichier1 fichier2 ...
La CI lui passe la liste des fichiers modifiés (git diff --name-only).
Il sort en erreur dès qu'un fichier dépasse le seuil.
"""

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-mo", type=float, default=5.0, help="seuil en Mo")
    parser.add_argument("fichiers", nargs="*")
    args = parser.parse_args()

    seuil = args.max_mo * 1024 * 1024
    trop_lourds = []
    for chemin in args.fichiers:
        if os.path.isfile(chemin) and os.path.getsize(chemin) > seuil:
            trop_lourds.append((chemin, os.path.getsize(chemin) / 1024 / 1024))

    for chemin, taille in trop_lourds:
        print(f"::error file={chemin}::{chemin} fait {taille:.1f} Mo (seuil {args.max_mo:g} Mo)")

    if trop_lourds:
        print(
            "Ces fichiers sont trop lourds pour Git (données brutes, parquet, zip...). "
            "Garde-les en dehors du dépôt, voir le .gitignore."
        )
        return 1
    print(f"OK, aucun fichier modifié ne dépasse {args.max_mo:g} Mo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
