
"""WP2 - Identification des accidents en France métropolitaine."""

DEPARTEMENTS_METROPOLE = {
    f"{i:02d}" for i in range(1, 96)
} - {"20"} | {"2A", "2B"}


def appliquer(t: dict) -> dict:
    resultat = dict(t)

    if "caracteristiques" in t:
        df = t["caracteristiques"].copy()

        dep = df["dep"].astype("string").str.strip().str.upper()

        # Corriger uniquement les codes numériques à un chiffre.
        # Exemples : "6" -> "06", "1" -> "01".
        # Ne pas modifier 2A, 2B ou les codes outre-mer.
        a_corriger = dep.str.fullmatch(r"[0-9]").fillna(False)
        dep_corrige = dep.where(~a_corriger, "0" + dep)

        # Conserver les autres valeurs d'origine dans la colonne dep.
        df["dep"] = df["dep"].where(~a_corriger, dep_corrige)

        # Recalculer l'indicateur après correction.
        df["metropole"] = dep_corrige.isin(DEPARTEMENTS_METROPOLE)

        resultat["caracteristiques"] = df

    return resultat
