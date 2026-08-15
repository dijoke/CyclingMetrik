---

description: "Task list for Import complet de l'historique Strava et conservation illimitée"
---

# Tasks: Import complet de l'historique Strava et conservation illimitée

**Input**: Design documents from `/specs/004-importer-intégralité-historique/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Incluses pour la pagination et le retry sur limite de débit du connecteur Strava — intégration externe couverte par le Principe IV (tests de contrat). Le retrait du job de purge (US2) est une suppression de code sans logique d'analyse à tester ; validé via `quickstart.md`.

**Organization**: Tasks are grouped by user story (US1 → US2, per spec.md priorities) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Paths : `backend/src/`, `backend/tests/` — feature backend-only (plan.md)

---

## Phase 1: Setup

- [X] T001 Confirmer qu'aucune nouvelle dépendance n'est nécessaire (research.md Decision 1/3) — `httpx` et la stdlib (`time.sleep`) suffisent

**Note** : pas de phase Foundational — US1 et US2 touchent des fichiers disjoints (`integrations/strava/connecteur.py` + `services/import_seances.py` pour US1 ; `jobs/purge_retention.py` + `main.py` pour US2) et ne partagent aucun prérequis bloquant.

---

## Phase 2: User Story 1 - Importer l'intégralité de mon historique Strava (Priority: P1) 🎯 MVP

**Goal**: La première synchronisation Strava importe la totalité de l'historique disponible (pagination), et une limite de débit temporaire ne fait pas échouer l'import silencieusement.

**Independent Test**: quickstart.md §Scénario US1 — connecter un compte Strava avec >100 activités et vérifier que `GET /api/seances` renvoie l'intégralité de l'historique, pas seulement 100/30 jours.

### Tests for User Story 1

- [X] T002 [P] [US1] Test de contrat : pagination multi-pages (mock 2-3 pages successives, vérifier l'agrégation complète) dans `backend/tests/contract/test_strava_connecteur.py` — écrit avant l'implémentation (Principe IV)
- [X] T003 [P] [US1] Test de contrat : retry automatique sur `429` puis succès (mock séquence 429→429→200) dans `backend/tests/contract/test_strava_connecteur.py`
- [X] T004 [P] [US1] Test de contrat : `429` persistant au-delà du nombre max de tentatives → lève `PlateformeIndisponibleError` dans `backend/tests/contract/test_strava_connecteur.py`

### Implementation for User Story 1

- [X] T005 [US1] Implémenter la pagination (boucle jusqu'à page incomplète) et le retry borné sur `429` dans `StravaConnecteur.recuperer_seances` (`backend/src/integrations/strava/connecteur.py`) (depends on T002-T004 ; research.md Decision 1/3)
- [X] T006 [US1] Adapter `importer_seances` : `depuis=None` pour la première synchronisation Strava uniquement (Garmin/Nolio inchangés) dans `backend/src/services/import_seances.py` (depends on T005 ; research.md Decision 2)

**Checkpoint**: User Story 1 fonctionnelle et testable indépendamment (quickstart §US1).

---

## Phase 3: User Story 2 - Conserver mes séances indéfiniment (Priority: P2)

**Goal**: Aucune séance n'est plus supprimée automatiquement, quelle que soit son ancienneté ; l'export/suppression RGPD explicite reste inchangé.

**Independent Test**: quickstart.md §Scénario US2 — constater qu'une séance de plus de 3 mois reste présente dans `GET /api/seances`, et que le job de purge n'est plus enregistré.

### Implementation for User Story 2

- [X] T007 [US2] Supprimer `backend/src/jobs/purge_retention.py` (research.md Decision 4)
- [X] T008 [US2] Retirer l'import et l'enregistrement du job de purge dans `backend/src/main.py` (depends on T007)

**Checkpoint**: User Stories 1 ET 2 fonctionnelles indépendamment.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T009 Rejouer `specs/001-coaching-velo-garmin-strava/quickstart.md` (US1 → US2 → US3 → export/suppression RGPD) — vérifier zéro régression fonctionnelle (FR-005)
- [X] T010 Run full quickstart.md (004) validation end-to-end (US1 → US2), y compris connexion du vrai compte Strava de l'utilisateur

**Checkpoint**: Feature complete, conforme au Principe IV et sans régression sur la spec 001.

> **Note on T009/T010** : suite pytest complète (38 tests : 30 de la feature 001 + 4 de pagination/retry US1 + 4 supplémentaires trouvés durant la validation en conditions réelles). Déployé via `docker compose` (backend + frontend + db), et validé avec **le vrai compte Strava de l'utilisateur** — 787 séances importées, du 2020-11-28 au 2026-08-15 (~6 ans d'historique), confirmant l'intégralité de l'import (US1, SC-001) et l'absence de purge (US2).
>
> Deux défauts réels, invisibles aux tests unitaires/contrat existants, ont été découverts et corrigés pendant cette validation live :
> 1. **Flux OAuth jamais réellement exercé de bout en bout** (bug préexistant de la feature 001) : `POST /api/connexions/{plateforme}/callback` attend une requête POST, mais Strava redirige le navigateur via GET — et le frontend n'avait aucune route pour intercepter ce redirect (seul `api.connexions.callback()` existait côté client, jamais appelé). Corrigé en ajoutant une page `ConnexionCallback.tsx` + route `/connexions/:plateforme/callback`, et en faisant pointer le `redirect_uri` OAuth vers le frontend (nouveau setting `FRONTEND_BASE_URL`, backend `src/api/connexions.py` + `src/config.py`) plutôt que vers le backend.
> 2. **Timeout httpx par défaut (5s) trop court** pour `GET /activities?per_page=100` en conditions réelles → `ReadTimeout` systématique, mal classifié en "Strava indisponible". Corrigé : timeout explicite à 30s, et le retry (déjà en place pour 429) étendu aux erreurs de transport transitoires — voir `test_recuperer_seances_retente_sur_timeout_transitoire`.
>
> Les deux corrections touchent uniquement le connecteur Strava et la connexion OAuth — aucun changement au périmètre fonctionnel de FR-001 à FR-006.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **User Story 1 (Phase 2)**: Depends on Setup only. No dependency on US2.
- **User Story 2 (Phase 3)**: Depends on Setup only. Indépendante de US1 (fichiers disjoints), même si sa valeur pratique est plus grande une fois US1 livrée (spec.md).
- **Polish (Phase 4)**: Depends on both user stories being complete.

### Within Each User Story

- US1 : tests avant implémentation (T002-T004 avant T005 — Principe IV).
- US2 : suppression directe, pas de tests dédiés (pas de logique d'analyse).

### Parallel Opportunities

- T002, T003, T004 (tests de contrat, même fichier mais cas indépendants) peuvent être écrits en parallèle puis exécutés ensemble.
- US1 et US2 peuvent être développées en parallèle par deux développeurs (fichiers totalement disjoints).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: User Story 1
3. **STOP and VALIDATE**: quickstart.md §US1 avec un vrai compte Strava
4. Demo : historique complet importé

### Incremental Delivery

1. Setup → US1 (import complet) → valider → demo
2. US2 (conservation illimitée) → valider → demo
3. Polish (non-régression 001 + validation bout-en-bout avec connexion réelle)

---

## Notes

- [P] tasks = fichiers différents ou cas de test indépendants, pas de dépendance.
- [Story] label mappe chaque tâche à sa user story pour la traçabilité.
- Commit après chaque tâche ou groupe logique.
