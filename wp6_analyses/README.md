# WP6 : analyses

Notebooks dans `notebooks/`. Pour charger les données :

```python
from wp2_nettoyage.pipeline import donnees_propres   # données nettoyées (recommandé)
from commun.recuperer_donnees import charger_tout    # ou données brutes
```

Lancez Jupyter depuis la racine du repo pour que ces imports fonctionnent.
Utilisez le découpage train/test du schéma `protocole` pour que les résultats soient comparables.
Videz les sorties volumineuses des notebooks avant de committer (aucune donnée sur GitHub).
