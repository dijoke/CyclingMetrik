# Quickstart : Import complet de l'historique Strava et conservation illimitée

**Feature**: `004-importer-intégralité-historique` | **Date**: 2026-08-15

## Prérequis

Identiques à `specs/001-coaching-velo-garmin-strava/quickstart.md` (backend + frontend démarrés, base PostgreSQL migrée, `STRAVA_CLIENT_ID`/`STRAVA_CLIENT_SECRET` renseignés dans `backend/.env`). Un compte Strava réel avec un historique de plus de 100 activités et/ou plus de 30 jours est nécessaire pour valider pleinement US1.

## Scénario US1 — Importer l'intégralité de mon historique Strava (P1)

**Correspond à**: spec.md Acceptance Scenarios 1-3 de US1, SC-001, SC-003.

1. Se connecter à Strava depuis la page Connexions (flux OAuth déjà existant, spec 001).
2. **Vérifier** : `GET /api/seances` renvoie, après la synchronisation initiale, un nombre d'activités cohérent avec la totalité de l'historique Strava du compte (comparer avec le nombre d'activités visible sur strava.com/athlete/training), pas seulement les 100 ou 30 derniers jours les plus récents.
3. Si le compte a plus de 100 activités, **vérifier** dans les logs backend que plusieurs pages ont été demandées (`page=1`, `page=2`, ...) plutôt qu'un seul appel.
4. (Optionnel, difficile à provoquer en conditions réelles) Simuler une réponse `429` de l'API Strava et vérifier que l'import reprend automatiquement (couvert par les tests de contrat, cf. `tests/contract/test_strava_connecteur.py`).

## Scénario US2 — Conserver mes séances indéfiniment (P2)

**Correspond à**: spec.md Acceptance Scenarios 1-2 de US2, SC-002.

1. Vérifier que `backend/src/jobs/purge_retention.py` n'existe plus et n'est plus enregistré dans `backend/src/main.py`.
2. Insérer (ou constater) une séance dont `date_debut` est antérieure à 3 mois.
3. **Vérifier** : cette séance reste présente dans `GET /api/seances` — aucune suppression automatique ne se produit.
4. **Vérifier** que `GET /api/athlete/export` et `DELETE /api/athlete` (RGPD, spec 001 FR-013) fonctionnent toujours normalement — la conservation illimitée automatique n'affecte pas le contrôle explicite de l'athlète sur ses données.

## Vérification de non-régression

Rejouer `specs/001-coaching-velo-garmin-strava/quickstart.md` (US1 → US2 → US3) pour confirmer que l'analyse de charge, les recommandations et l'export/suppression RGPD continuent de fonctionner avec un historique de séances plus volumineux.
