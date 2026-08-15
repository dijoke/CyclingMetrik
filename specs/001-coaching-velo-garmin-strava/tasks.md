---

description: "Task list for Coaching vélo connecté (import séances + conseils récupération/nutrition)"
---

# Tasks: Coaching vélo connecté (import séances + conseils récupération/nutrition)

**Input**: Design documents from `/specs/001-coaching-velo-garmin-strava/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included for training-load calculation, the recommendation engine, and platform integrations — mandated by Constitution Principle IV (test-first on analysis logic, contract tests for external integrations). CRUD/plumbing tasks do not get dedicated test tasks beyond that.

**Organization**: Tasks are grouped by user story (US1 → US2 → US3, per spec.md priorities) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths follow the web-app structure from plan.md: `backend/src/`, `backend/tests/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create `backend/` and `frontend/` directory structure per plan.md (Project Structure section)
- [X] T002 Initialize backend Python 3.12 project in `backend/pyproject.toml` with FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, httpx, APScheduler, `cryptography`, pytest, pytest-asyncio
- [X] T003 [P] Initialize frontend Vite + React 18 + TypeScript project in `frontend/package.json` with React Query, Recharts, Vitest, React Testing Library
- [X] T004 [P] Configure backend linting/formatting (ruff + black) in `backend/pyproject.toml`
- [X] T005 [P] Configure frontend linting/formatting (eslint + prettier) in `frontend/.eslintrc`, `frontend/.prettierrc`
- [X] T006 [P] Create `backend/.env.example` documenting `DATABASE_URL`, `TOKEN_ENCRYPTION_KEY`, `GARMIN_CLIENT_ID`/`SECRET`, `STRAVA_CLIENT_ID`/`SECRET`, `NOLIO_CLIENT_ID`/`SECRET` — no real secrets committed (constitution: Contraintes & Confidentialité)

**Checkpoint**: Project scaffolding exists for both backend and frontend.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Setup PostgreSQL connection, SQLAlchemy engine/session factory in `backend/src/db.py`
- [X] T008 Setup Alembic migrations framework in `backend/alembic/` (depends on T007)
- [X] T009 [P] Create `Athlete` model in `backend/src/models/athlete.py` (data-model.md §Athlete)
- [X] T010 [P] Create `ConnexionPlateforme` model in `backend/src/models/connexion_plateforme.py` (data-model.md §ConnexionPlateforme)
- [X] T011 [P] Create `Seance` model in `backend/src/models/seance.py` (data-model.md §Seance)
- [X] T012 [P] Create `ChargeEntrainement` model in `backend/src/models/charge_entrainement.py` (data-model.md §ChargeEntrainement)
- [X] T013 [P] Create `Recommandation` model in `backend/src/models/recommandation.py` (data-model.md §Recommandation)
- [X] T014 Generate initial Alembic migration covering all models (depends on T009-T013)
- [X] T015 Implement token encryption utility (Fernet, at-rest OAuth token encryption, Principe II) in `backend/src/security/token_crypto.py`
- [X] T016 Setup FastAPI app skeleton and API router structure in `backend/src/main.py` and `backend/src/api/__init__.py`
- [X] T017 Setup error handling and structured logging middleware in `backend/src/api/middleware.py`
- [X] T018 Setup APScheduler skeleton (no jobs registered yet) in `backend/src/jobs/scheduler.py` (depends on T016)
- [X] T019 [P] Define `PlateformeConnecteur` protocol, `SeanceBrute` dataclass, `TokenInvalideError`, `PlateformeIndisponibleError` in `backend/src/integrations/base.py` (contracts/plateforme-connecteur.md)
- [X] T020 [P] Setup frontend API client base and React Query provider in `frontend/src/services/api_client.ts`
- [X] T021 [P] Setup frontend routing and page shell (Connexions, Historique, Dashboard, Recommandations, Profil) in `frontend/src/App.tsx` and `frontend/src/pages/`

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Importer automatiquement mes séances (Priority: P1) 🎯 MVP

**Goal**: L'athlète connecte Garmin Connect, Strava et/ou Nolio ; ses séances sont importées automatiquement (historique + nouvelles), et il est averti si une connexion devient invalide.

**Independent Test**: quickstart.md §Scénario US1 — connecter un compte de test, vérifier l'import des 30 derniers jours en < 5 min (SC-001), vérifier qu'une nouvelle séance apparaît sous 24h (SC-002), vérifier la notification en cas de token expiré/révoqué (FR-009). Testable sans dashboard ni recommandations.

### Tests for User Story 1

- [X] T022 [P] [US1] Contract test for Strava connector against fixtures in `backend/tests/contract/test_strava_connecteur.py` (contracts/plateforme-connecteur.md)
- [X] T023 [P] [US1] Contract test for Garmin Connect connector against fixtures in `backend/tests/contract/test_garmin_connecteur.py`
- [X] T024 [P] [US1] Contract test for Nolio connector against fixtures in `backend/tests/contract/test_nolio_connecteur.py`
- [X] T025 [P] [US1] Integration test: OAuth connect + initial import flow in `backend/tests/integration/test_import_seances.py` (quickstart US1 steps 1-4)
- [X] T026 [P] [US1] Integration test: token expiration/revocation → statut `expire`/`revoque` + notification (FR-009) in `backend/tests/integration/test_connexion_expiree.py`

### Implementation for User Story 1

- [X] T027 [P] [US1] Implement Strava connector (OAuth 2.0, `recuperer_seances`, `rafraichir_token`) in `backend/src/integrations/strava/connecteur.py` (depends on T019, T022)
- [X] T028 [P] [US1] Implement Garmin Connect connector (OAuth PKCE) in `backend/src/integrations/garmin/connecteur.py` (depends on T019, T023)
- [X] T029 [P] [US1] Implement Nolio connector in `backend/src/integrations/nolio/connecteur.py` (depends on T019, T024)
- [X] T030 [US1] Implement import service: normalize `SeanceBrute` → `Seance`, dedupe by (`connexion_plateforme_id`, `id_externe`), flag `aberrant` per validation rules in `backend/src/services/import_seances.py` (depends on T011, T027-T029)
- [X] T031 [US1] Implement cross-platform duplicate detection (research.md §7) in `backend/src/services/detection_doublons.py` (depends on T030)
- [X] T032 [US1] Implement connexions API routes (`GET /api/connexions`, `POST .../autoriser`, `POST .../callback`, `DELETE .../{plateforme}`) in `backend/src/api/connexions.py` (depends on T010, T015, T027-T029)
- [X] T033 [US1] Implement `GET /api/seances` route with `depuis`/`statut_donnees` filters in `backend/src/api/seances.py` (depends on T030, T031)
- [X] T034 [US1] Register periodic sync job (poll active connections every 15 min; `TokenInvalideError` → statut `expire`; `PlateformeIndisponibleError` → defer to next cycle) in `backend/src/jobs/sync_seances.py` (depends on T018, T030)
- [X] T035 [P] [US1] Frontend: Connexions page (connect/disconnect per platform, status badges, reconnect prompt) in `frontend/src/pages/Connexions.tsx` (depends on T020, T032)
- [X] T036 [P] [US1] Frontend: Historique séances page (chronological list, duplicate/aberrant badges) in `frontend/src/pages/HistoriqueSeances.tsx` (depends on T020, T033)

**Checkpoint**: User Story 1 fully functional and independently testable (quickstart §US1 passes end-to-end).

---

## Phase 4: User Story 2 - Comprendre ma charge d'entraînement et mon état de forme (Priority: P2)

**Goal**: Le tableau de bord traduit les séances importées en charge d'entraînement (aiguë/chronique, ACWR), signale une tendance de surcharge, et indique explicitement une insuffisance de données plutôt qu'une analyse trompeuse.

**Independent Test**: quickstart.md §Scénario US2 — charger un historique de séances (via fixtures ou US1) et vérifier `charge_aigue_7j`/`charge_chronique_28j`/`tendance`/`donnees_suffisantes` sur `GET /api/dashboard/charge`. Testable indépendamment de US1 (import) et US3 (recommandations).

### Tests for User Story 2

- [X] T037 [P] [US2] Unit tests for training-load calculation (ACWR, tendance thresholds, `donnees_suffisantes` gating) in `backend/tests/unit/test_training_load.py` — write first, must fail before implementation (Principe IV)
- [X] T038 [P] [US2] Contract test for `GET /api/dashboard/charge` in `backend/tests/contract/test_dashboard_charge.py`
- [X] T039 [P] [US2] Integration test: surcharge and insufficient-data scenarios in `backend/tests/integration/test_dashboard_charge.py` (quickstart US2)

### Implementation for User Story 2

- [X] T040 [US2] Implement training-load calculation service (charge_aigue_7j, charge_chronique_28j, ratio_acwr, tendance, donnees_suffisantes) in `backend/src/services/training_load/calcul_charge.py` (depends on T037, T011)
- [X] T041 [US2] Persist `ChargeEntrainement` snapshots on recompute in `backend/src/services/training_load/snapshot.py` (depends on T012, T040)
- [X] T042 [US2] Register periodic recompute job in `backend/src/jobs/recompute_charge.py` (depends on T018, T041)
- [X] T043 [US2] Implement `GET /api/dashboard/charge` route in `backend/src/api/dashboard.py` (depends on T040)
- [X] T044 [P] [US2] Frontend: Dashboard page with load chart and 4-week trend (Recharts) in `frontend/src/pages/Dashboard.tsx` (depends on T020, T043)
- [X] T045 [P] [US2] Frontend: surcharge / insufficient-data visual states in `frontend/src/components/ChargeIndicator.tsx` (depends on T044)

**Checkpoint**: User Stories 1 AND 2 both independently functional.

---

## Phase 5: User Story 3 - Recevoir des conseils de récupération et nutrition (Priority: P3)

**Goal**: Après une séance significative, l'athlète reçoit une recommandation de récupération et une estimation nutritionnelle explicables, ou un message explicite d'insuffisance de données (jamais une estimation non fondée — Principe I NON-NEGOTIABLE).

**Independent Test**: quickstart.md §Scénario US3 — simuler une séance à forte charge avec profil complet, vérifier une recommandation `disponible` avec justification sous 2 min (SC-005) ; répéter avec profil vide et vérifier `statut = donnees_insuffisantes` avec motif explicite.

### Tests for User Story 3

- [X] T046 [P] [US3] Unit tests for the `Recommandation` invariant (`disponible` ⟺ `contenu` + `justification` non nuls ; `donnees_insuffisantes` ⟺ `contenu` nul + `motif_donnees_insuffisantes` renseigné) in `backend/tests/unit/test_recommandations.py` — write first (Principe I NON-NEGOTIABLE, Principe IV)
- [X] T047 [P] [US3] Unit tests for nutrition estimation formulas (calories, glucides/protéines/lipides) in `backend/tests/unit/test_nutrition.py`
- [X] T048 [P] [US3] Integration test: recommendation generation after a significant séance + insufficient-profile case in `backend/tests/integration/test_recommandations.py` (quickstart US3)

### Implementation for User Story 3

- [X] T049 [US3] Implement recovery recommendation rules engine in `backend/src/services/recommendations/recuperation.py` (depends on T046, T040)
- [X] T050 [US3] Implement nutrition estimation rules engine in `backend/src/services/recommendations/nutrition.py` (depends on T047, T040)
- [X] T051 [US3] Implement recommendation orchestration enforcing the insufficient-data guard in `backend/src/services/recommendations/moteur.py` (depends on T013, T049, T050)
- [X] T052 [US3] Trigger recommendation generation on significant séance import (≤ 2 min, SC-005) in `backend/src/jobs/generer_recommandations.py` (depends on T030, T051)
- [X] T053 [US3] Implement `GET /api/recommandations` route (with `type` filter) in `backend/src/api/recommandations.py` (depends on T051)
- [X] T054 [US3] Implement `GET`/`PUT /api/athlete/profil` routes in `backend/src/api/athlete.py` (depends on T009)
- [X] T055 [P] [US3] Frontend: Recommandations page (recovery + nutrition cards, insufficient-data messaging) in `frontend/src/pages/Recommandations.tsx` (depends on T020, T053)
- [X] T056 [P] [US3] Frontend: Profil athlète page (weight, height, goals, dietary constraints form) in `frontend/src/pages/Profil.tsx` (depends on T020, T054)

**Checkpoint**: All three user stories (US1, US2, US3) independently functional — MVP complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: RGPD compliance, retention, and hardening that spans all user stories

- [X] T057 [P] Implement `GET /api/athlete/export` (full JSON export: profil, séances, connexions, recommandations — RGPD, FR-013) in `backend/src/api/athlete.py` (depends on T009-T013)
- [X] T058 Implement `DELETE /api/athlete` (cascade delete + revoke active OAuth tokens, RGPD) in `backend/src/api/athlete.py` (depends on T027-T029 `revoquer`, T057)
- [X] T059 Implement 3-month rolling retention purge job (FR-012) in `backend/src/jobs/purge_retention.py` (depends on T018, T011)
- [X] T060 [P] Verify no plaintext OAuth token storage anywhere (code review + grep for raw token fields) — Principe II
- [X] T061 [P] Update `README.md` with backend/frontend setup and run instructions
- [ ] T062 Run full quickstart.md validation end-to-end (US1 → US2 → US3 → RGPD export/delete scenario)

**Checkpoint**: Feature complete, constitution-compliant, and validated against quickstart.md.

> **Note on T062**: all other tasks were verified by static/build checks — `ruff check` (backend), `tsc -b` + `eslint` + `vite build` (frontend), and a live FastAPI app import whose generated OpenAPI schema was diffed against `contracts/api.openapi.yaml` (all 11 endpoints match). The `pytest` suite (unit/contract/integration, T022-T048) requires a running PostgreSQL instance; this environment's Docker daemon has no outbound network access, so the containerized test DB could not be started and the suite has not actually been executed. Run `alembic upgrade head && pytest` against a real Postgres (see quickstart.md prerequisites) to complete T062 before merging.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational only. No dependency on US2/US3.
- **User Story 2 (Phase 4)**: Depends on Foundational only. Independently testable via fixtures without US1's live import pipeline; in practice consumes `Seance` rows that US1 produces.
- **User Story 3 (Phase 5)**: Depends on Foundational and on the training-load service from US2 (T040) — recommendations use recent charge to decide recovery/nutrition. Independently testable via fixtures without US1/US2's UI.
- **Polish (Phase 6)**: Depends on all three user stories being complete (export/delete touch every entity; purge job touches `Seance`).

### User Story Dependencies

- **US1 (P1)**: No dependencies on other stories — true MVP entry point.
- **US2 (P2)**: Functionally independent (testable with seeded fixtures), but delivers real value only once US1 supplies live `Seance` data.
- **US3 (P3)**: Reuses the training-load calculation service (T040) from US2 as an internal dependency, per research.md's charge-based recommendation model — this is a code dependency, not a UI/test dependency; US3 remains independently testable per its own quickstart scenario.

### Within Each User Story

- Tests before implementation (Principe IV, TDD for analysis logic and contract tests for integrations).
- Connectors/models before services; services before API routes; API routes before frontend pages.
- Story complete and checkpoint-validated before moving to the next priority.

### Parallel Opportunities

- All Setup tasks marked [P] (T003-T006) run in parallel.
- All Foundational model tasks marked [P] (T009-T013) run in parallel; T019-T021 in parallel with those.
- Once Foundational completes, US1, US2, US3 backend work can proceed in parallel across developers — but note US3's T049/T050 need T040 (US2) merged first if truly parallelized by different people.
- Within US1: the three connector implementations (T027-T029) and their contract tests (T022-T024) are independent per-platform and fully parallelizable.
- Frontend pages within each story ([P]-marked) can be built in parallel with that story's backend once the relevant API contract is stable.

---

## Parallel Example: User Story 1

```bash
# Contract tests for the three platform connectors, in parallel:
Task: "Contract test for Strava connector in backend/tests/contract/test_strava_connecteur.py"
Task: "Contract test for Garmin Connect connector in backend/tests/contract/test_garmin_connecteur.py"
Task: "Contract test for Nolio connector in backend/tests/contract/test_nolio_connecteur.py"

# Connector implementations, in parallel (different files, same shared interface):
Task: "Implement Strava connector in backend/src/integrations/strava/connecteur.py"
Task: "Implement Garmin Connect connector in backend/src/integrations/garmin/connecteur.py"
Task: "Implement Nolio connector in backend/src/integrations/nolio/connecteur.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run quickstart.md §US1 independently
5. Demo: séances importées automatiquement depuis Garmin/Strava/Nolio

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → validate via quickstart §US1 → demo (MVP)
3. Add US2 → validate via quickstart §US2 → demo (charge d'entraînement)
4. Add US3 → validate via quickstart §US3 → demo (recommandations)
5. Polish (RGPD export/delete, retention purge) → validate full quickstart.md

### Parallel Team Strategy

With multiple developers, after Foundational is done:

- Developer A: US1 (3 connectors + import pipeline)
- Developer B: US2 (training-load service + dashboard) — can start immediately, only needs seeded `Seance` fixtures, not a finished US1
- Developer C: starts US3 test-writing (T046-T048) early, but implementation (T049-T050) waits on US2's T040

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Tests are included only where the constitution mandates them (analysis logic, integrations) — Principe IV.
- Commit after each task or logical group.
- Stop at any checkpoint to validate a story independently before continuing.
