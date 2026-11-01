"""Étape d'exemple : renvoie les tables inchangées.

Comment écrire une étape :
- un fichier par étape, nommé eNNN_nom.py (NNN = numéro, de 10 en 10 pour pouvoir en insérer) ;
- une fonction appliquer(t) qui reçoit le dict {"caracteristiques", "lieux", "usagers", "vehicules"}
  de DataFrames et renvoie un dict de même forme ;
- travailler sur des copies (df = t["usagers"].copy()) plutôt que modifier les DataFrames reçus ;
- une étape = une transformation (ex. e110_types : convertir les colonnes numériques,
  e120_coordonnees : lat/long "47,56" -> 47.56, e130_manquants : -1 et "" -> NA) ;
- ajouter le nom du module dans ORDRE de pipeline.py.

Exemple :
    def appliquer(t):
        t = dict(t)
        u = t["usagers"].copy()
        u["grav"] = u["grav"].astype(int)
        t["usagers"] = u
        return t
"""


def appliquer(t: dict) -> dict:
    return t
