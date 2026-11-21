# CI niveau 1

À chaque PR vers `main`, GitHub lance 4 vérifications et affiche un statut vert ou rouge :

| Job | Outil | Ce qu'il vérifie |
|---|---|---|
| Python | ruff | lint + format, seulement sur les `.py` modifiés dans la PR |
| SQL | sqlfluff (postgres) | lint des `.sql` modifiés (vert s'il n'y en a pas) |
| Secrets | gitleaks | pas de mot de passe ou de clé dans les commits de la PR |
| Fichiers lourds | petit script Python | aucun fichier modifié au-dessus de 5 Mo |

On ne contrôle que ce que la PR touche : le code déjà là n'est pas vérifié tant qu'on n'y
met pas la main, sinon toutes les PR seraient rouges dès le début.

## Tester en local avant de pousser

```bash
pip install ruff==0.8.6 sqlfluff==3.3.0
ruff check mon_fichier.py
ruff format mon_fichier.py      # corrige directement le format
sqlfluff lint mon_fichier.sql
python .github/scripts/fichiers_lourds.py --max-mo 5 fichier1 fichier2
```

La config est dans `ruff.toml`, `.sqlfluff` et `.gitleaks.toml`.
Si gitleaks signale un faux positif, ajouter le chemin dans l'allowlist de `.gitleaks.toml`.
