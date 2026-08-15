---

description: "Task list for Restructuration du design (mode sombre, navigation, vue d'ensemble)"
---

# Tasks: Restructuration du design (mode sombre, navigation, vue d'ensemble)

**Input**: Design documents from `/specs/006-restructuration-design-mode/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Aucune tâche de test dédiée — feature strictement de présentation/navigation, aucune nouvelle logique de calcul (Principe IV non applicable, cf. plan.md). Validation via `quickstart.md`.

**Organization**: Tasks are grouped by user story (US1 → US2 → US3, per spec.md priorities).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths : `frontend/src/` — feature frontend-only (plan.md)

---

## Phase 1: Setup

- [X] T001 Confirmer qu'aucune nouvelle dépendance n'est nécessaire (research.md) — CSS natif, React state, `localStorage`

---

## Phase 2: User Story 1 - Choisir un thème clair ou sombre (Priority: P1) 🎯 MVP

**Goal**: L'utilisateur bascule entre thème clair et sombre ; son choix est mémorisé ; à défaut, la préférence système est suivie.

**Independent Test**: quickstart.md §US1.

### Implementation for User Story 1

- [X] T002 [P] [US1] Étendre `frontend/src/styles/tokens.css` avec les valeurs sombres (`@media (prefers-color-scheme: dark)` + `[data-theme="dark"]`, research.md Decision 1)
- [X] T003 [P] [US1] Créer le hook `frontend/src/hooks/useTheme.ts` (lecture `localStorage`/`prefers-color-scheme`, application de `data-theme` sur `<html>`, écriture au changement — research.md Decision 3)
- [X] T004 [US1] Créer `frontend/src/components/ThemeToggle.tsx` et l'intégrer dans la navigation existante (depends on T003)
- [X] T005 [US1] Étendre `frontend/src/components/TrendChart.tsx` et `frontend/src/components/VolumeBarChart.tsx` avec les paires de couleurs clair/dark (depends on T002 ; research.md Decision 2)

**Checkpoint**: User Story 1 fonctionnelle et testable indépendamment (quickstart §US1).

---

## Phase 3: User Story 2 - Naviguer via une barre de navigation moderne (Priority: P2)

**Goal**: Navigation horizontale en haut de l'écran, remplaçant la sidebar, avec mise en évidence de la page active.

**Independent Test**: quickstart.md §US2.

### Implementation for User Story 2

- [X] T006 [US2] Restructurer `frontend/src/App.tsx` : remplacer la sidebar par une barre horizontale (`<header>`), réintégrer `ThemeToggle` dans la nouvelle navigation (depends on T004 ; research.md Decision 4)

**Checkpoint**: User Stories 1 ET 2 fonctionnelles indépendamment.

---

## Phase 4: User Story 3 - Voir un aperçu global dès l'ouverture du tableau de bord (Priority: P3)

**Goal**: Tuiles KPI (charge actuelle, volume de l'année en cours, un record) en haut du tableau de bord, avant le détail existant.

**Independent Test**: quickstart.md §US3.

### Implementation for User Story 3

- [X] T007 [US3] Frontend : section tuiles KPI dans `frontend/src/pages/Dashboard.tsx`, composant depuis `GET /api/dashboard/charge`, `GET /api/statistiques/comparaison-annuelle`, `GET /api/statistiques/records` (data-model.md ; aucune donnée manquante affichée sans indication explicite, FR-007)

**Checkpoint**: Les 3 user stories sont fonctionnelles indépendamment.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T008 Rejouer `specs/001-coaching-velo-garmin-strava/quickstart.md`, `specs/002-améliore-design-application/quickstart.md`, `specs/004-importer-intégralité-historique/quickstart.md` et `specs/005-exploiter-les-années/quickstart.md` — vérifier zéro régression (FR-008)
- [X] T009 Run full quickstart.md (006) validation end-to-end, y compris vérification de contraste en thème sombre sur les 6 pages

**Checkpoint**: Feature complete, sans régression.

> **Note on T008/T009** : suite pytest backend inchangée, 44/44 toujours verte (aucun fichier backend touché par cette feature). Déployé via `docker compose` et capturé via Chromium headless dans les deux thèmes (clair/sombre × 6 pages = 12 captures) — zéro erreur console. Bascule de thème et persistance après rechargement vérifiées par script (`document.documentElement.dataset.theme` conservé après `page.reload()`). Les graphiques (Recharts) ont été vérifiés par inspection directe du DOM/SVG plutôt que par lecture visuelle des captures : à deux reprises la capture d'écran compressée donnait l'impression erronée de barres/lignes manquantes en thème sombre, alors que `getBoundingClientRect()`/attributs `fill`/`stroke` confirmaient un rendu correct (hauteurs et couleurs conformes aux données réelles) — enseignement noté pour les validations futures : privilégier l'inspection DOM à la lecture d'image compressée pour les graphiques SVG.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **User Story 1 (Phase 2)**: Depends on Setup only.
- **User Story 2 (Phase 3)**: Dépend de T004 (US1) car le contrôle de thème doit exister avant d'être replacé dans la nouvelle navigation — seule dépendance inter-story de cette feature.
- **User Story 3 (Phase 4)**: Depends on Setup only — indépendante de US1/US2, mais s'intègre visuellement mieux une fois la navigation restructurée.
- **Polish (Phase 5)**: Depends on all three user stories.

### Parallel Opportunities

- T002/T003 (US1, fichiers différents) en parallèle.
- US3 (T007) peut être développée en parallèle de US1/US2 par un autre développeur — dépendance uniquement visuelle, pas technique.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Setup
2. User Story 1 (mode sombre)
3. **STOP and VALIDATE**: quickstart.md §US1
4. Demo : bascule clair/sombre fonctionnelle

### Incremental Delivery

1. Setup → US1 (mode sombre) → valider → demo
2. US2 (navigation top-bar) → valider → demo
3. US3 (vue d'ensemble) → valider → demo
4. Polish → validation complète + non-régression

---

## Notes

- [P] tasks = fichiers différents, pas de dépendance.
- Commit après chaque tâche ou groupe logique.
