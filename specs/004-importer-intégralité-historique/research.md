# Research: Import complet de l'historique Strava et conservation illimitée

**Feature**: `004-importer-intégralité-historique` | **Date**: 2026-08-15

État constaté du code avant décision : `StravaConnecteur.recuperer_seances` (`backend/src/integrations/strava/connecteur.py`) fait un seul appel `GET /athlete/activities?after=...&per_page=100` — aucune pagination, donc au-delà de 100 activités le reste est silencieusement ignoré. `import_seances.py` retombe sur `depuis = now - 30 jours` quand `date_derniere_synchronisation` est `None` (première synchronisation). `purge_retention.py` supprime tout `Seance.date_debut` antérieur à 90 jours, via un job cron quotidien enregistré dans `main.py`.

## Decision 1 — Pagination : boucle interne au connecteur Strava, pas de nouvel endpoint

**Rationale** : L'API Strava pagine via `page`/`per_page` (max 200, on garde 100 comme aujourd'hui). La solution la plus simple est une boucle dans `StravaConnecteur.recuperer_seances` qui incrémente `page` jusqu'à ce qu'une page renvoie moins de `per_page` résultats — sans changement d'interface (`PlateformeConnecteur.recuperer_seances` continue de renvoyer `list[SeanceBrute]`, appelant `import_seances.py` inchangé sur ce point).

**Alternatives considered** :
- Exposer une pagination côté API applicative (`GET /api/seances?page=`) — rejeté : hors périmètre, la pagination Strava est un problème d'intégration interne, pas une exigence utilisateur.
- Import asynchrone via une tâche de fond dédiée avec suivi de progression — rejeté par le Principe V (Simplicité) : un appel connecteur qui boucle en interne suffit pour un usage mono-athlète ; une file de tâches ajouterait une dépendance et une complexité opérationnelle non justifiées à ce stade.

## Decision 2 — Première synchronisation Strava : `depuis=None` (pas de borne), spécifique à Strava

**Rationale** : FR-001 exige l'import complet lors de la première connexion. `import_seances.py` retombe actuellement sur `now - 30 jours` pour toute plateforme quand `date_derniere_synchronisation` est `None`. Les connecteurs Garmin (`depuis.timestamp()`) et Nolio (`depuis.isoformat()`) plantent si `depuis` est `None` — cette feature étant scopée à Strava (Assumptions de `spec.md`), le fallback devient conditionnel à la plateforme : `None` uniquement pour Strava, la logique existante (30 jours) restant inchangée pour Garmin/Nolio afin de ne pas les casser alors qu'ils ne sont pas modifiés par cette feature.

**Alternatives considered** :
- Changer le fallback pour toutes les plateformes et adapter Garmin/Nolio en conséquence — rejeté : hors périmètre demandé par l'utilisateur (Strava uniquement), et ces connecteurs ne sont pas utilisés en pratique aujourd'hui (pas de compte connecté) donc aucun bénéfice immédiat à les toucher.

## Decision 3 — Limite de débit Strava : retry avec backoff borné dans le connecteur, dégradation vers `PlateformeIndisponibleError`

**Rationale** : Strava limite à 100 requêtes/15 min et 1000/jour par application. Un historique volumineux (plusieurs centaines/milliers d'activités) peut dépasser la limite courte le temps d'un import initial. Le connecteur retente automatiquement sur `HTTP 429` avec une pause fixe (60s) jusqu'à un nombre de tentatives borné (16 ≈ 16 minutes, couvrant la réinitialisation de la fenêtre de 15 min). Si la limite est toujours atteinte après ce délai (cas de la limite journalière), le connecteur lève `PlateformeIndisponibleError` (type déjà existant) — le job périodique existant (`sync_seances.py`) l'attrape déjà et journalise sans faire échouer les autres connexions, et reporte au cycle suivant (15 min). Grâce à la vérification d'existence par `id_externe` déjà en place dans `import_seances.py` (idempotent), relancer l'import au cycle suivant ne duplique rien — seules les activités déjà connues sont ignorées, le reste reprend.

**Alternatives considered** :
- Suivi explicite de la position de pagination entre cycles (reprise exacte page par page) — rejeté par le Principe V : la ré-exécution idempotente déjà garantie par la contrainte d'unicité (`id_externe`) rend un mécanisme de reprise dédié inutile pour ce volume (mono-athlète).
- Respecter un header `Retry-After` — non applicable : Strava n'envoie pas ce header sur ses 429 (seulement `X-RateLimit-Limit`/`X-RateLimit-Usage`) ; un backoff fixe borné est plus simple et suffisant.

## Decision 4 — Suppression complète du job de purge (pas de flag de configuration)

**Rationale** : FR-004 retire la purge automatique. Plutôt que d'ajouter un flag `RETENTION_ENABLED` (complexité conditionnelle non demandée), le fichier `backend/src/jobs/purge_retention.py` et son enregistrement dans `main.py` sont supprimés — code mort retiré plutôt que désactivé (cohérent avec la préférence du projet pour ne pas garder de mécanismes de compatibilité inutilisés).

**Alternatives considered** :
- Garder le job avec une rétention configurable très longue (ex. 10 ans) — rejeté : n'est pas une "conservation illimitée" au sens strict demandé par l'utilisateur, et ajoute un paramètre de configuration sans bénéfice réel.

## Résumé des NEEDS CLARIFICATION

Aucun — la spec ne portait aucun marqueur `[NEEDS CLARIFICATION]`.
