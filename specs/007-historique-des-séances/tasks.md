---

description: "Task list for Historique des séances enrichi (filtres, détail, records de puissance)"
---

# Tasks: Historique des séances enrichi (filtres, détail, records de puissance)

**Input**: Design documents from `/specs/007-historique-des-séances/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Incluses pour la fonction de calcul de records de puissance (`services/puissance/records.py`) — fonction pure, logique de calcul au sens du Principe IV, écrite avant l'implémentation. Le reste (schémas, endpoints, job, frontend) est de la plomberie/présentation, validée via `quickstart.md`.

**Organization**: Tasks are grouped by user story (US1 → US2 → US3, per spec.md priorities).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths : `backend/src/`, `backend/tests/`, `frontend/src/`

---

## Phase 1: Setup

- [X] T001 Confirmer qu'aucune nouvelle dépendance n'est nécessaire (research.md) — `httpx`, SQLAlchemy/Alembic, `react-router-dom` déjà présents

---

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T002 [P] Migration Alembic : 6 colonnes nullable sur `seance` (`puissance_max_1min` … `_20min`, `flux_puissance_traite_le`) + modèle `Seance` étendu dans `backend/src/models/seance.py` (data-model.md)
- [X] T003 [P] Étendre `SeanceOut` avec les 5 champs `puissance_max_*` dans `backend/src/api/schemas.py` (data-model.md)

**Checkpoint**: Schéma prêt — US2 et US3 peuvent l'utiliser.

---

## Phase 3: User Story 1 - Filtrer et trier mes séances (Priority: P1) 🎯 MVP

**Goal**: Trier/filtrer l'historique par colonne (date, durée, distance, dénivelé, puissance, statut).

**Independent Test**: quickstart.md §US1.

### Implementation for User Story 1

- [X] T004 [US1] Frontend : en-têtes de colonnes triables (clic = tri, second clic = inversion) et filtres (plage de dates, statut) dans `frontend/src/pages/HistoriqueSeances.tsx`

**Checkpoint**: User Story 1 fonctionnelle et testable indépendamment (quickstart §US1). Ne dépend pas de Foundational (aucune donnée nouvelle utilisée).

---

## Phase 4: User Story 2 - Consulter le détail d'une séance (Priority: P2)

**Goal**: Cliquer sur une séance ouvre une page dédiée avec ses métriques complètes.

**Independent Test**: quickstart.md §US2.

### Implementation for User Story 2

- [X] T005 [US2] Endpoint `GET /api/seances/{id}` (404 si absente/n'appartient pas à l'athlète) dans `backend/src/api/seances.py` (depends on T003 ; contracts/api-seance-detail.yaml)
- [X] T006 [P] [US2] Frontend : nouvelle page `frontend/src/pages/SeanceDetail.tsx` + route `/seances/:id` dans `frontend/src/App.tsx`
- [X] T007 [US2] Frontend : lignes de `HistoriqueSeances.tsx` cliquables, navigation vers `/seances/:id` (depends on T004, T006)

**Checkpoint**: User Stories 1 ET 2 fonctionnelles indépendamment.

---

## Phase 5: User Story 3 - Records de puissance par durée (Priority: P3)

**Goal**: Calculer et afficher, pour chaque séance avec capteur de puissance, les 5 meilleures puissances moyennes (1/3/5/10/20 min), avec backfill complet de l'historique.

**Independent Test**: quickstart.md §US3.

### Tests for User Story 3

- [X] T008 [US3] Test unitaire `calculer_records_puissance` (fenêtre glissante correcte, `null` si séance plus courte qu'une durée, `null` si flux vide) dans `backend/tests/unit/test_records_puissance.py` — écrit avant l'implémentation (Principe IV)

### Implementation for User Story 3

- [X] T009 [US3] Implémenter `calculer_records_puissance` (fonction pure) dans `backend/src/services/puissance/records.py` (depends on T008 ; research.md Decision 3)
- [X] T010 [US3] Implémenter `recuperer_flux_puissance` dans `backend/src/integrations/strava/connecteur.py`, réutilisant le retry/backoff existant (research.md Decision 3/4)
- [X] T011 [US3] Implémenter le job de fond `backend/src/jobs/calculer_records_puissance.py` (lot borné, marquage `flux_puissance_traite_le`, skip sans appel réseau si pas de puissance moyenne) (depends on T002, T009, T010 ; research.md Decision 4)
- [X] T012 [US3] Enregistrer le nouveau job dans `backend/src/main.py` (depends on T011)
- [X] T013 [P] [US3] Frontend : afficher les 5 records (ou absence explicite) sur `frontend/src/pages/SeanceDetail.tsx` (depends on T006, T003)
- [X] T014 [US3] Frontend : colonne records de puissance dans `HistoriqueSeances.tsx`, triable (depends on T004, T003)

**Checkpoint**: Les 3 user stories sont fonctionnelles indépendamment.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T015 Rejouer les quickstart.md des features 001, 002, 004 et 005 — vérifier zéro régression (FR-009)
- [X] T016 Run full quickstart.md (007) validation end-to-end sur les données réelles, vérifier la progression du backfill

**Checkpoint**: Feature complete, conforme au Principe IV, sans régression.

> **Note on T015/T016** : suite pytest complète, 52/52 verte (44 précédents + 5 pour `calculer_records_puissance` + 3 tests de contrat pour `recuperer_flux_puissance`, tous écrits avant leur implémentation respective). Déployé via `docker compose` sur les données réelles (787 séances) : migration appliquée sans erreur (up/down/up vérifié), endpoint de détail testé (200 sur séance existante, 404 sur UUID inexistant), premier lot de 20 séances backfillé manuellement pour valider le pipeline de bout en bout — résultats physiologiquement cohérents (ex. 219W/1min → 165W/20min, décroissance attendue). Le job planifié (toutes les 2 min, confirmé enregistré au démarrage : `traiter_lot_records_puissance`) poursuit le backfill des 767 séances restantes en tâche de fond. Capturé via Chromium headless : tri, filtre, navigation vers le détail, et page 404 tous fonctionnels, zéro erreur console (hors le 404 réseau attendu du test lui-même).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS US2/US3 (schéma requis) ; US1 n'en dépend pas.
- **User Story 1 (Phase 3)**: Depends on Setup only.
- **User Story 2 (Phase 4)**: Depends on Foundational. T007 dépend aussi de T004 (US1) — seule dépendance inter-story, car les lignes cliquables s'ajoutent au tableau déjà trié/filtré.
- **User Story 3 (Phase 5)**: Depends on Foundational. T014 dépend aussi de T004 (US1, même fichier).
- **Polish (Phase 6)**: Depends on all three user stories.

### Parallel Opportunities

- T002/T003 (Foundational) en parallèle.
- T006/T013 (US2/US3, fichiers différents une fois Foundational fait) en parallèle.
- US1 peut être développée entièrement en parallèle de Foundational/US2/US3 (aucune dépendance).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Setup
2. User Story 1 (tri/filtre)
3. **STOP and VALIDATE**: quickstart.md §US1
4. Demo : historique triable/filtrable

### Incremental Delivery

1. Setup + Foundational → schéma prêt
2. US1 → valider → demo (tri/filtre)
3. US2 → valider → demo (page de détail)
4. US3 → valider → demo (records de puissance, backfill en cours)
5. Polish → validation complète + non-régression

---

## Notes

- [P] tasks = fichiers différents, pas de dépendance.
- Commit après chaque tâche ou groupe logique.
