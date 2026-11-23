-- WP3-04 : table de référence des codes BAAC (libellés FR + EN)
-- Source : wp2_nettoyage/metadata/codifications/modalites_baac_finalisees.csv (WP2, non modifié)
--          + notice ONISR anglaise du 21/10/2025 pour label_en
-- Données : wp3_entrepot/donnees/ref_modalites.csv (295 codes, séparateur ;)
-- Exécuté par construire.py (seul script autorisé à écrire dans entrepot).
-- Relançable : la table est supprimée puis recréée.
-- Pour un essai sur une base de test : remplacer entrepot par test.

DROP TABLE IF EXISTS entrepot.ref_modalites;

CREATE TABLE entrepot.ref_modalites (
    -- colonnes du WP2, dans leur ordre d'origine, non modifiées
    famille           TEXT NOT NULL,
    variable          TEXT NOT NULL,
    code              TEXT NOT NULL,   -- texte : actp contient les codes A et B
    effectif_total    INTEGER,
    annees_presentes  INTEGER,
    libelle           TEXT NOT NULL,   -- libellé français (WP2)
    type              TEXT,
    statut            TEXT,
    source            TEXT,
    annees            TEXT,
    remarque          TEXT,
    -- colonnes ajoutées par le WP3
    label_en          TEXT NOT NULL,   -- libellé anglais
    note_traduction   TEXT,            -- vide = repris de la notice ONISR anglaise ou simple retouche de forme
    PRIMARY KEY (variable, code)       -- garantit qu'il n'y a aucun doublon
);

-- Le contenu est chargé depuis ref_modalites.csv par construire.py.

-- Vérifications après chargement :
-- SELECT COUNT(*) FROM entrepot.ref_modalites;                                      -- 295
-- SELECT famille, COUNT(*) FROM entrepot.ref_modalites GROUP BY famille ORDER BY famille;  -- 36 / 57 / 91 / 111
-- SELECT variable, code, libelle, label_en, note_traduction
-- FROM entrepot.ref_modalites WHERE note_traduction <> '' ORDER BY variable, code;
