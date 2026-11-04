"""WP7 - Tâche A : analyse des liens entre variables (et avec la gravité).

Objectif : repérer les variables redondantes entre elles et celles qui sont liées
à la gravité, pour aider à choisir les variables du K-NN (tâche D).

Une mesure adaptée à chaque type de paire, toutes comprises entre 0 et 1 :
    numérique  - numérique   : |Spearman|            (relation monotone, robuste aux valeurs extrêmes)
    catégorielle - catégorielle : V de Cramér corrigé  (khi-deux, correction de Bergsma 2013)
    numérique  - catégorielle : rapport de corrélation η (part de variance expliquée par la catégorie)

Les variables BAAC sont pour la plupart des CODES (ex. atm = 2 : pluie légère) :
elles sont catégorielles même si elles s'écrivent avec des chiffres.

L'analyse est faite uniquement sur la partie ENTRAÎNEMENT, pour ne pas choisir
les variables en regardant les données de test.

Lancement depuis la racine du repo :
    python -m wp7_analyses.analyse_liens
    python -m wp7_analyses.analyse_liens --echantillon 200000   (plus rapide)

Sorties (dossier wp7_analyses/sorties/, jamais envoyé sur GitHub) :
    matrice_liens.csv, heatmap_liens.png, liens_avec_gravite.csv,
    paires_redondantes.csv, resume.md
"""
import argparse
import itertools
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, spearmanr

from wp2_nettoyage.pipeline import donnees_propres

SORTIES = Path(__file__).resolve().parent / "sorties"
GRAINE = 42
SEUIL_REDONDANCE = 0.5

# Variables numériques (de vraies quantités)
NUMERIQUES = ["age", "vma", "nbv", "heure"]

# Variables catégorielles (codes BAAC), regroupées par table d'origine
CATEGORIELLES = [
    # caractéristiques de l'accident
    "mois", "jour_semaine", "lum", "agg", "int", "atm", "col", "dep",
    # lieu
    "catr", "circ", "vosp", "prof", "plan", "surf", "infra", "situ",
    # véhicule
    "senc", "catv", "obs", "obsm", "choc", "manv", "motor",
    # usager
    "place", "catu", "sexe", "trajet", "secu1", "locp", "actp", "etatp",
]
CIBLE = "grave"

VALEURS_MANQUANTES = {"", "-1", "None", "N/A", "nan", "NaN", "(1)", " "}


# --------------------------------------------------------------------------- préparation
def _normaliser_codes(serie):
    """Texte -> code propre : espaces retirés, '06' et '6' unifiés, valeurs vides -> NA."""
    s = serie.astype("string").str.replace("\xa0", "", regex=False).str.strip()
    s = s.mask(s.isin(VALEURS_MANQUANTES))
    num = pd.to_numeric(s, errors="coerce")
    est_entier = num.notna() & (num == num.round())
    s = s.where(~est_entier, num.round().astype("Int64").astype("string"))
    return s


def _cle_vehicule(serie):
    return serie.astype("string").str.replace("\xa0", "", regex=False).str.replace(" ", "", regex=False).str.strip()


def preparation_provisoire(t):
    """Assemble une ligne par usager avec les infos de l'accident, du lieu et du véhicule.

    PROVISOIRE : tant que le nettoyage du WP2 n'est pas terminé, on fait ici le minimum
    (unifier les codes, NA pour -1, quelques bornes de vraisemblance). À alléger quand
    donnees_propres() renverra des données déjà typées et nettoyées.
    """
    car = t["caracteristiques"].copy()
    lieux = t["lieux"].copy()
    veh = t["vehicules"].copy()
    usa = t["usagers"].copy()

    for df in (car, lieux, veh, usa):
        df["num_acc"] = df["num_acc"].astype("string").str.strip()
    veh["id_vehicule"] = _cle_vehicule(veh["id_vehicule"])
    usa["id_vehicule"] = _cle_vehicule(usa["id_vehicule"])

    # Plusieurs lignes "lieux" pour certains accidents : on garde la première
    lieux = lieux.drop_duplicates("num_acc", keep="first")

    # Date et heure
    jour = pd.to_numeric(car["jour"], errors="coerce")
    mois = pd.to_numeric(car["mois"], errors="coerce")
    an = pd.to_numeric(car["an"], errors="coerce")
    dates = pd.to_datetime(pd.DataFrame({"year": an, "month": mois, "day": jour}), errors="coerce")
    car["jour_semaine"] = dates.dt.day_of_week.astype("Int64").astype("string")
    car["mois"] = mois.astype("Int64").astype("string")
    car["heure"] = pd.to_numeric(car["hrmn"].astype("string").str.split(":").str[0], errors="coerce")

    cols_car = ["num_acc", "mois", "jour_semaine", "heure", "lum", "agg", "int", "atm", "col", "dep"]
    cols_lieux = ["num_acc", "catr", "circ", "vosp", "prof", "plan", "surf", "infra", "situ", "vma", "nbv"]
    cols_veh = ["num_acc", "id_vehicule", "senc", "catv", "obs", "obsm", "choc", "manv", "motor"]
    cols_usa = ["num_acc", "id_vehicule", "annee", "an_nais", "grav",
                "place", "catu", "sexe", "trajet", "secu1", "locp", "actp", "etatp"]

    df = (usa[cols_usa]
          .merge(veh[cols_veh], on=["num_acc", "id_vehicule"], how="left")
          .merge(car[cols_car], on="num_acc", how="left")
          .merge(lieux[cols_lieux], on="num_acc", how="left"))

    # Numériques
    df["age"] = pd.to_numeric(df["annee"], errors="coerce") - pd.to_numeric(df["an_nais"], errors="coerce")
    df.loc[(df["age"] < 0) | (df["age"] > 110), "age"] = np.nan
    df["vma"] = pd.to_numeric(df["vma"], errors="coerce")
    df.loc[(df["vma"] < 5) | (df["vma"] > 130), "vma"] = np.nan
    df["nbv"] = pd.to_numeric(df["nbv"], errors="coerce")
    df.loc[(df["nbv"] < 1) | (df["nbv"] > 12), "nbv"] = np.nan

    # Catégorielles
    for c in CATEGORIELLES:
        df[c] = _normaliser_codes(df[c])

    # Cible : grave = tué (2) ou hospitalisé (3) ; non grave = indemne (1) ou blessé léger (4)
    grav = _normaliser_codes(df["grav"])
    df[CIBLE] = grav.map({"2": "1", "3": "1", "1": "0", "4": "0"}).astype("string")

    return df[["num_acc"] + NUMERIQUES + CATEGORIELLES + [CIBLE]]


def partie_entrainement(df):
    """Garde les 80 % d'entraînement.

    PROVISOIRE : découpage local par accident (un même accident n'est jamais à la fois
    en entraînement et en test), graine 42. À remplacer par le découpage commun du
    schéma `protocole` dès qu'il est documenté, pour être aligné avec les WP5 et WP6.
    """
    accidents = np.sort(df["num_acc"].dropna().unique())
    rng = np.random.default_rng(GRAINE)
    test = set(rng.choice(accidents, size=int(0.2 * len(accidents)), replace=False))
    return df[~df["num_acc"].isin(test)]


# --------------------------------------------------------------------------- mesures
def v_cramer(x, y):
    """V de Cramér avec correction de biais (Bergsma, 2013)."""
    m = pd.crosstab(x, y)
    if m.shape[0] < 2 or m.shape[1] < 2:
        return np.nan
    chi2 = chi2_contingency(m, correction=False)[0]
    n = m.to_numpy().sum()
    r, k = m.shape
    phi2 = chi2 / n
    phi2c = max(0.0, phi2 - (k - 1) * (r - 1) / (n - 1))
    rc = r - (r - 1) ** 2 / (n - 1)
    kc = k - (k - 1) ** 2 / (n - 1)
    denom = min(kc - 1, rc - 1)
    return float(np.sqrt(phi2c / denom)) if denom > 0 else np.nan


def rapport_correlation(categories, valeurs):
    """η : racine de la part de variance de `valeurs` expliquée par `categories`."""
    d = pd.DataFrame({"c": categories, "v": valeurs}).dropna()
    if d["c"].nunique() < 2:
        return np.nan
    moy = d["v"].mean()
    ss_tot = ((d["v"] - moy) ** 2).sum()
    if ss_tot == 0:
        return np.nan
    g = d.groupby("c")["v"].agg(["mean", "size"])
    ss_inter = (g["size"] * (g["mean"] - moy) ** 2).sum()
    return float(np.sqrt(ss_inter / ss_tot))


def spearman_abs(x, y):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(d) < 3:
        return np.nan
    return float(abs(spearmanr(d["x"], d["y"]).statistic))


def lien(df, a, b):
    """Choisit la mesure selon le type des deux variables (paires sans valeur manquante)."""
    num_a, num_b = a in NUMERIQUES, b in NUMERIQUES
    if num_a and num_b:
        return spearman_abs(df[a], df[b]), "Spearman"
    if num_a != num_b:
        cat, num = (b, a) if num_a else (a, b)
        return rapport_correlation(df[cat], df[num]), "eta"
    d = df[[a, b]].dropna()
    return v_cramer(d[a], d[b]), "Cramer"


def matrice_liens(df, variables):
    m = pd.DataFrame(np.eye(len(variables)), index=variables, columns=variables)
    mesures = {}
    for a, b in itertools.combinations(variables, 2):
        valeur, mesure = lien(df, a, b)
        m.loc[a, b] = m.loc[b, a] = valeur
        mesures[(a, b)] = mesure
    return m, mesures


# --------------------------------------------------------------------------- sorties
def heatmap(m, fichier):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    masque = np.triu(np.ones_like(m, dtype=bool), k=1)
    fig, ax = plt.subplots(figsize=(20, 17))
    sns.heatmap(m.astype(float), mask=masque, cmap="Blues", vmin=0, vmax=1, square=True,
                annot=True, fmt=".2f", annot_kws={"size": 6}, linewidths=0.3,
                cbar_kws={"label": "force du lien (0 = aucun, 1 = parfait)", "shrink": 0.6}, ax=ax)
    ax.set_title("Liens entre variables (|Spearman|, V de Cramér, η) - partie entraînement", fontsize=14)
    fig.tight_layout()
    fig.savefig(fichier, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--echantillon", type=int, default=0,
                        help="nombre de lignes tirées au hasard (0 = toute la partie entraînement)")
    args = parser.parse_args()
    debut = time.time()
    SORTIES.mkdir(exist_ok=True)

    print("Chargement et préparation des données...")
    df = preparation_provisoire(donnees_propres())
    df = df[df[CIBLE].notna()]
    train = partie_entrainement(df)
    if args.echantillon and args.echantillon < len(train):
        train = train.sample(args.echantillon, random_state=GRAINE)
    print(f"  {len(df)} usagers avec gravité connue, {len(train)} utilisés (entraînement)")
    print(f"  part de cas graves : {(train[CIBLE] == '1').mean():.1%}")

    variables = NUMERIQUES + CATEGORIELLES + [CIBLE]
    print(f"Calcul des liens entre {len(variables)} variables...")
    m, mesures = matrice_liens(train, variables)
    m.round(4).to_csv(SORTIES / "matrice_liens.csv", sep=";", decimal=",")
    heatmap(m, SORTIES / "heatmap_liens.png")

    # Lien de chaque variable avec la gravité
    cible = (m[CIBLE].drop(CIBLE).rename("lien_avec_gravite").sort_values(ascending=False).to_frame())
    cible["mesure"] = [mesures.get((v, CIBLE), mesures.get((CIBLE, v))) for v in cible.index]
    cible["taux_manquant"] = [train[v].isna().mean() for v in cible.index]
    cible.round(4).to_csv(SORTIES / "liens_avec_gravite.csv", sep=";", decimal=",")

    # Paires redondantes (hors cible)
    paires = [(a, b, m.loc[a, b], mesures[(a, b)])
              for (a, b) in mesures if CIBLE not in (a, b) and m.loc[a, b] >= SEUIL_REDONDANCE]
    redond = pd.DataFrame(paires, columns=["variable_1", "variable_2", "lien", "mesure"])
    redond = redond.sort_values("lien", ascending=False)
    redond.round(4).to_csv(SORTIES / "paires_redondantes.csv", sep=";", decimal=",", index=False)

    # Résumé lisible
    lignes = ["# Analyse des liens entre variables (WP7, tâche A)", "",
              f"- Usagers utilisés (partie entraînement) : {len(train)}",
              f"- Part de cas graves : {(train[CIBLE] == '1').mean():.1%}",
              f"- Seuil de redondance : {SEUIL_REDONDANCE}", "",
              "## Variables les plus liées à la gravité", "",
              "| Variable | Lien | Mesure | Manquants |", "|---|---|---|---|"]
    for v, r in cible.iterrows():
        lignes.append(f"| {v} | {r['lien_avec_gravite']:.3f} | {r['mesure']} | {r['taux_manquant']:.1%} |")
    lignes += ["", f"## Paires redondantes (lien >= {SEUIL_REDONDANCE})", ""]
    if redond.empty:
        lignes.append("Aucune.")
    else:
        lignes += ["| Variable 1 | Variable 2 | Lien | Mesure |", "|---|---|---|---|"]
        lignes += [f"| {r.variable_1} | {r.variable_2} | {r.lien:.3f} | {r.mesure} |" for r in redond.itertuples()]
    (SORTIES / "resume.md").write_text("\n".join(lignes), encoding="utf-8")

    print("\nTop 10 des variables liées à la gravité :")
    print(cible.head(10).round(3).to_string())
    print(f"\n{len(redond)} paire(s) redondante(s) (lien >= {SEUIL_REDONDANCE})")
    if not redond.empty:
        print(redond.head(15).round(3).to_string(index=False))
    print(f"\nRésultats dans {SORTIES}  ({time.time() - debut:.0f} s)")


if __name__ == "__main__":
    main()
