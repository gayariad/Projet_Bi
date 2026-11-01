# Se connecter à la base

Vous avez reçu **en privé** une URL de la forme :

```
postgresql+psycopg://lecture:MOTDEPASSE@HOTE/neondb?sslmode=require
```

On y lit les informations de connexion :

| Information | Valeur |
|---|---|
| Hôte | `HOTE` (la partie entre `@` et `/`) |
| Port | `5432` |
| Base | `neondb` |
| Utilisateur | `lecture` |
| Mot de passe | `MOTDEPASSE` (entre `lecture:` et `@`) |
| SSL | obligatoire (`require`) |

Le compte `lecture` peut tout lire mais ne peut rien modifier. **Ne partagez jamais cette URL**
(ni sur GitHub, ni dans un notebook, ni dans une capture d'écran).

---

## 1. DBeaver (explorer les tables en SQL)

1. Installer DBeaver Community : <https://dbeaver.io/download/>.
2. **Base de données > Nouvelle connexion**, choisir **PostgreSQL**, puis **Suivant**.
   (DBeaver propose de télécharger le pilote la première fois : accepter.)
3. Onglet **Principal** :
   - Hôte : `HOTE`
   - Port : `5432`
   - Base de données : `neondb`
   - Authentification : *Database Native*
   - Nom d'utilisateur : `lecture`
   - Mot de passe : `MOTDEPASSE` (cocher *Enregistrer le mot de passe* si vous le souhaitez)
4. Onglet **SSL** : cocher *Utiliser SSL*, mode SSL : **require**.
5. **Tester la connexion**, puis **Terminer**.
6. Dans l'arborescence : `neondb > Schémas > brut_2024 > Tables > usagers`. Ouvrir un éditeur SQL
   (clic droit > Éditeur SQL) et essayer :

   ```sql
   SELECT grav, count(*) FROM brut_2024.usagers GROUP BY grav ORDER BY grav;
   ```

Si la connexion échoue : vérifier que SSL est bien activé, et que le mot de passe a été copié sans espace.

---

## 2. Python (charger les données dans pandas)

Depuis la racine du repo, après l'installation décrite dans le `README.md` :

1. Copier `.env.exemple` en `.env`.
2. Dans `.env`, remplacer la ligne `URL_LECTURE=...` par l'URL reçue. Le fichier `.env` est ignoré
   par git : il ne partira jamais sur GitHub.
3. Tester :

   ```bash
   python -m commun.recuperer_donnees
   ```

   Vous devez voir les 4 tables avec leurs nombres de lignes et les années 2019-2024.

4. Dans un script ou un notebook (lancé depuis la racine du repo) :

   ```python
   from commun.recuperer_donnees import charger_tout

   t = charger_tout()              # dict de 4 DataFrames
   usagers = t["usagers"]          # toutes les années, colonne "annee" ajoutée
   usagers.head()
   ```

   Le premier appel lit la base (quelques dizaines de secondes) et crée un cache dans `cache/`.
   Les suivants sont instantanés. Pour relire la base : `charger_tout(rafraichir=True)`.

   Toutes les colonnes sont du texte : c'est le rôle du WP2 de les typer.
   Pour les données nettoyées : `from wp2_nettoyage.pipeline import donnees_propres`.

---

## 3. Power BI Desktop (connecteur PostgreSQL)

1. **Accueil > Obtenir les données > Plus… > Base de données PostgreSQL**, puis **Se connecter**.
2. Serveur : `HOTE` — Base de données : `neondb`. Mode : *Importer*. **OK**.
3. Fenêtre d'identification : onglet **Base de données**, utilisateur `lecture`, mot de passe `MOTDEPASSE`.
   **Se connecter**.
4. Si Power BI demande une connexion chiffrée, laisser le chiffrement activé (Neon l'exige).
5. Dans le navigateur, cocher les tables du schéma `entrepot` (les tables `brut_*` sont en texte,
   à éviter pour les rapports), puis **Charger**.

Les identifiants sont stockés par Power BI Desktop sur votre poste, pas dans le projet `.pbip` :
le projet peut donc être commité. Pour les modifier : **Fichier > Options et paramètres >
Paramètres de la source de données**.

En cas d'erreur de certificat ou de pilote : mettre Power BI Desktop à jour (le pilote PostgreSQL
Npgsql est inclus dans les versions récentes).
