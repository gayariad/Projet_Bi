
"""WP2 - Signalement des doublons sans suppression."""


def appliquer(t: dict) -> dict:
    resultat = dict(t)

    if "usagers" in t:
        df = t["usagers"].copy()

        # Comparer les données métier sans l'identifiant technique.
        # Exclure aussi le marqueur s'il existe déjà
        # pour permettre plusieurs exécutions du nettoyage.
        colonnes_comparaison = [
            col for col in df.columns
            if col not in {"id_usager", "doublon_suspect"}
        ]

        if not colonnes_comparaison:
            raise ValueError(
                "Aucune colonne disponible pour détecter les doublons."
            )

        # Signaler toutes les lignes appartenant à un groupe
        # de doublons, sans supprimer d'observations.
        df["doublon_suspect"] = df.duplicated(
            subset=colonnes_comparaison,
            keep=False
        )

        resultat["usagers"] = df

    return resultat
