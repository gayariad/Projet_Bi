"""Table d'analyse commune WP5/WP6/WP7, selon le protocole commun.

    from wp5_analyses.preparation import table_analyse
    ta = table_analyse()
    ta.X_app, ta.X_test, ta.y_app, ta.y_test   # index = num_acc
    ta.table                                    # table lisible, avant encodage
    ta.empreinte                                # empreinte des num_acc du test
"""
import hashlib
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

GRAINE = 42
PART_TEST = 0.2
NON_RENSEIGNE = "non_renseigne"
EMPREINTE_REFERENCE = "99915bbe74e3"

# codes ONISR
GRAV_GRAVE = [2, 3]
SECU_AUCUN = 0
CATU_PIETON = 3
CATV_DEUX_ROUES = [2, 30, 31, 32, 33, 34]
CATV_POIDS_LOURD = [13, 14, 15, 16, 17]

CATEGORIELLES = [
    "lum", "agg", "int", "atm", "col", "tranche_horaire", "jour_semaine", "mois", "an",
    "catr", "circ", "vosp", "prof", "plan", "surf", "infra", "situ",
]
NUMERIQUES = ["nbv", "vma"]
NON_RENSEIGNE_NUM = [f"{c}_non_renseigne" for c in NUMERIQUES]
INDICATEURS = ["pieton", "sans_equipement", "deux_roues", "poids_lourd"]
HORS_MODELE = ["dep", "com", "lat", "long", "jour"]
CIBLE = "grave"
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
TRANCHES = {"00h_06h": (0, 6), "06h_10h": (6, 10), "10h_16h": (10, 16),
            "16h_20h": (16, 20), "20h_24h": (20, 24)}


def _au_moins_un(df, masque, index):
    return masque.groupby(df["num_acc"]).any().reindex(index, fill_value=False).astype(int)


def _tranche_horaire(heure):
    tranche = pd.Series(pd.NA, index=heure.index, dtype="string")
    for nom, (debut, fin) in TRANCHES.items():
        tranche[(heure >= debut) & (heure < fin)] = nom
    return tranche


def construire_table(tables=None):
    """Une ligne par accident de métropole, index num_acc."""
    if tables is None:
        from wp2_nettoyage.pipeline import donnees_propres
        tables = donnees_propres()

    car = tables["caracteristiques"]
    car = car[car["metropole"].fillna(False).astype(bool)].set_index("num_acc").sort_index()
    idx = car.index
    lieu = tables["lieux"].loc[lambda d: d["lieu_principal"]].set_index("num_acc").reindex(idx)
    usa, veh = tables["usagers"], tables["vehicules"]
    t = pd.DataFrame(index=idx)

    suspectes = car["coordonnees_suspectes"].fillna(False).astype(bool)
    t["dep"], t["com"] = car["dep"], car["com"]
    t["lat"] = car["lat"].astype("Float64").mask(suspectes)
    t["long"] = car["long"].astype("Float64").mask(suspectes)

    for col in ["lum", "agg", "int", "atm", "col"]:
        t[col] = car[col]
    heure = pd.to_numeric(car["hrmn"].str[:2], errors="coerce")
    t["tranche_horaire"] = _tranche_horaire(heure)
    date = pd.to_datetime(pd.DataFrame({"year": car["an"], "month": car["mois"], "day": car["jour"]}),
                          errors="coerce")
    t["jour_semaine"] = date.dt.day_of_week.map(dict(enumerate(JOURS)))
    t["jour"], t["mois"], t["an"] = car["jour"], car["mois"], car["an"]

    for col in ["catr", "circ", "vosp", "prof", "plan", "surf", "infra", "situ"]:
        t[col] = lieu[col]
    t["nbv"] = lieu["nbv"].astype("Float64")
    t["vma"] = lieu["vma"].mask(lieu["vma_suspecte"].fillna(False).astype(bool)).astype("Float64")
    for col in NUMERIQUES:
        t[f"{col}_non_renseigne"] = t[col].isna().astype(int)

    t["pieton"] = _au_moins_un(usa, usa["catu"].eq(CATU_PIETON).fillna(False), idx)
    t["sans_equipement"] = _au_moins_un(usa, usa["secu1"].eq(SECU_AUCUN).fillna(False), idx)
    t["deux_roues"] = _au_moins_un(veh, veh["catv"].isin(CATV_DEUX_ROUES), idx)
    t["poids_lourd"] = _au_moins_un(veh, veh["catv"].isin(CATV_POIDS_LOURD), idx)
    t[CIBLE] = _au_moins_un(usa, usa["grav"].isin(GRAV_GRAVE), idx)
    return t


def decouper(table):
    """80/20 entrainement/test , tri préalable pour un tirage indépendant de l'ordre."""
    table = table.sort_index()
    return train_test_split(table, test_size=PART_TEST, random_state=GRAINE,
                            stratify=table[CIBLE])


def empreinte(index):
    return hashlib.sha256(",".join(sorted(map(str, index))).encode()).hexdigest()[:12]


def verifier_empreinte(valeur, reference=None):
    reference = EMPREINTE_REFERENCE if reference is None else reference
    if reference is not None and valeur != reference:
        raise ValueError(f"Empreinte du test {valeur} != référence {reference} : "
                         "le test n'est pas le même que celui des autres WP.")


def _en_categories(df):
    return df.astype("string").fillna(NON_RENSEIGNE).astype(object)


def _en_float(df):
    return df.astype("float64")


def creer_preparateur():
    categorielles = Pipeline([
        ("texte", FunctionTransformer(_en_categories, feature_names_out="one-to-one")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False, dtype=np.int8)),
    ])
    numeriques = Pipeline([
        ("float", FunctionTransformer(_en_float, feature_names_out="one-to-one")),
        ("moyenne", SimpleImputer(strategy="mean")),
        ("echelle", StandardScaler()),
    ])
    return ColumnTransformer([
        ("cat", categorielles, CATEGORIELLES),
        ("num", numeriques, NUMERIQUES),
        ("bin", "passthrough", NON_RENSEIGNE_NUM + INDICATEURS),
    ], verbose_feature_names_out=False).set_output(transform="pandas")


@dataclass
class TableAnalyse:
    X_app: pd.DataFrame
    X_test: pd.DataFrame
    y_app: pd.Series
    y_test: pd.Series
    preparateur: ColumnTransformer
    table: pd.DataFrame
    empreinte: str


def table_analyse(tables=None):
    """Découpe, puis ajuste le préparateur sur l'apprentissage seulement."""
    table = construire_table(tables)
    app, test = decouper(table)
    prep = creer_preparateur()
    X_app = prep.fit_transform(app)
    X_test = prep.transform(test)
    valeur = empreinte(test.index)
    if tables is None:
        verifier_empreinte(valeur)
    return TableAnalyse(X_app, X_test, app[CIBLE], test[CIBLE], prep, table, valeur)


def main():
    ta = table_analyse()
    t = ta.table
    print(f"accidents          {len(t):>8}")
    print(f"apprentissage      {len(ta.X_app):>8}  part grave {ta.y_app.mean():.3f}")
    print(f"test               {len(ta.X_test):>8}  part grave {ta.y_test.mean():.3f}")
    print(f"colonnes encodées  {ta.X_app.shape[1]:>8}")
    print(f"empreinte du test  {ta.empreinte:>12}")
    print(f"piéton & sans équipement {int((t['pieton'] & t['sans_equipement']).sum()):>8}"
          f" / piéton {int(t['pieton'].sum())}")


if __name__ == "__main__":
    main()
