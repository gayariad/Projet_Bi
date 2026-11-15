"""WP2 - Signalement des doublons sans suppression."""


def appliquer(t: dict) -> dict:
    resultat = dict(t)

    if "usagers" in t:
        df = t["usagers"].copy()
        df["doublon_suspect"] = df.duplicated(keep=False)
        resultat["usagers"] = df

    return resultat
