"""Lit le Google Sheet des pseudos GitHub et invite chaque pseudo comme collaborateur (droit Write).

Les pseudos déjà collaborateurs ou déjà invités sont sautés. GitHub limite à 50 invitations
par 24 h : le surplus part automatiquement aux passages suivants.
"""
import csv
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["INVITE_TOKEN"]
SHEET_ID = os.environ["SHEET_ID"]
API = "https://api.github.com"
PSEUDO_VALIDE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def appel(methode, chemin, corps=None):
    req = urllib.request.Request(
        API + chemin,
        method=methode,
        data=json.dumps(corps).encode() if corps is not None else None,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            texte = r.read().decode()
            return r.status, json.loads(texte) if texte else None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def tous(chemin):
    page, res = 1, []
    while True:
        statut, donnees = appel("GET", f"{chemin}?per_page=100&page={page}")
        if statut != 200:
            sys.exit(f"Erreur {statut} sur {chemin} : {donnees}")
        res += donnees
        if len(donnees) < 100:
            return res
        page += 1


def lire_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    with urllib.request.urlopen(url) as r:
        lignes = list(csv.reader(io.StringIO(r.read().decode("utf-8"))))
    if not lignes:
        return []
    entete = [c.lower() for c in lignes[0]]
    col = next((i for i, c in enumerate(entete) if "github" in c), None)
    if col is None:
        sys.exit("Colonne « Pseudo GitHub » introuvable dans le Sheet.")
    pseudos = []
    for ligne in lignes[1:]:
        if col < len(ligne):
            p = ligne[col].strip().lstrip("@")
            p = re.sub(r"^https?://(www\.)?github\.com/", "", p).strip("/")
            if p:
                pseudos.append(p)
    return pseudos


def main():
    deja = {c["login"].lower() for c in tous(f"/repos/{REPO}/collaborators")}
    deja |= {i["invitee"]["login"].lower() for i in tous(f"/repos/{REPO}/invitations") if i.get("invitee")}

    envoyees = 0
    for p in dict.fromkeys(lire_sheet()):
        if p.lower() in deja:
            continue
        if not PSEUDO_VALIDE.match(p):
            print(f"::warning::Pseudo invalide ignoré : {p!r}")
            continue
        statut, rep = appel("PUT", f"/repos/{REPO}/collaborators/{p}", {"permission": "push"})
        if statut in (201, 204):
            print(f"Invité : {p}")
            deja.add(p.lower())
            envoyees += 1
        elif statut == 404:
            print(f"::warning::Pseudo GitHub introuvable : {p}")
        elif statut == 422 and "limit" in str(rep).lower():
            print("Limite de 50 invitations / 24 h atteinte, la suite partira plus tard.")
            break
        else:
            print(f"::warning::Échec pour {p} ({statut}) : {rep}")
    print(f"Invitations envoyées ce passage : {envoyees}")


if __name__ == "__main__":
    main()
