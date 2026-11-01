# WP2 : nettoyage

`pipeline.donnees_propres()` lit les tables brutes (`commun.recuperer_donnees.charger_tout()`)
puis applique, dans l'ordre de la liste `ORDRE`, chaque étape de `etapes/`.

```python
from wp2_nettoyage.pipeline import donnees_propres
t = donnees_propres()      # dict de 4 DataFrames nettoyés
```

## Ajouter une étape

1. Créer `etapes/eNNN_nom.py` avec une fonction `appliquer(t: dict) -> dict`
   (voir `etapes/e100_exemple.py`).
2. Ajouter `"eNNN_nom"` dans `ORDRE` (`pipeline.py`).
3. Lancer `pytest` depuis la racine du repo.
