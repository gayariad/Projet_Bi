
"""WP2 - Correction et signalement des valeurs hors plage sans suppression."""

import pandas as pd


VMA_A_CORRIGER = {300, 500, 700, 900}


def appliquer(t: dict) -> dict:
    resultat = dict(t)

    if "caracteristiques" in t:
        df = t["caracteristiques"].copy()

        lat = pd.to_numeric(df["lat"], errors="coerce")
        lon = pd.to_numeric(df["long"], errors="coerce")

        anomalies_coordonnees = (
            ((lat == 0) & (lon == 0))
            | (lat.notna() & ~lat.between(-90, 90))
            | (lon.notna() & ~lon.between(-180, 180))
        ).fillna(False)

        if "coordonnees_suspectes" in df.columns:
            anomalies_coordonnees |= (
                df["coordonnees_suspectes"].fillna(False).astype(bool)
            )

        df["coordonnees_suspectes"] = anomalies_coordonnees

        resultat["caracteristiques"] = df

    if "lieux" in t:
        df = t["lieux"].copy()

        vma = pd.to_numeric(df["vma"], errors="coerce")

        # Identifier les anomalies avant la correction.
        valeurs_a_corriger = vma.isin(VMA_A_CORRIGER)

        hors_plage = (
            (vma < 10) | (vma > 130)
        ).fillna(False)

        # Conserver les signalements existants si le module
        # est exécuté une seconde fois.
        if "vma_suspecte" in df.columns:
            hors_plage |= df["vma_suspecte"].fillna(False).astype(bool)

        # Corriger uniquement 300, 500, 700 et 900.
        # Garder le type numérique nullable existant.
        df["vma"] = df["vma"].mask(
            valeurs_a_corriger,
            vma // 10
        )

        # La valeur corrigée reste signalée comme suspecte.
        df["vma_suspecte"] = hors_plage | valeurs_a_corriger

        resultat["lieux"] = df

    return resultat
