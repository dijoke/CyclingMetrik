# Data Model: Import complet de l'historique Strava et conservation illimitée

**Feature**: `004-importer-intégralité-historique` | **Date**: 2026-08-15

Aucune nouvelle entité, aucun changement de schéma de base de données. Cette feature modifie exclusivement :

1. **Le comportement d'import** (`Séance`, `Connexion plateforme` — entités déjà définies dans `specs/001-coaching-velo-garmin-strava/data-model.md`) : la borne temporelle de la première synchronisation Strava change (illimitée au lieu de 30 jours), et l'appel à l'API Strava pagine désormais en interne.
2. **La planification** : le job `purge_retention` (`Seance.date_debut` > 90 jours → suppression) est retiré. Aucune table, colonne ou contrainte n'est modifiée par ce retrait — seul le code du job disparaît.

Aucun `data-model.md` de delta supplémentaire n'est nécessaire au-delà de cette note.
