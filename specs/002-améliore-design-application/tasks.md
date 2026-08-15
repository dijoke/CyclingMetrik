---

description: "Task list for Refonte visuelle de l'application"
---

# Tasks: Refonte visuelle de l'application

**Input**: Design documents from `/specs/002-améliore-design-application/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Incluses uniquement pour l'extension backend `historique_charge()` — c'est de la logique d'analyse, couverte par le Principe IV (NON-NEGOTIABLE, test-first). Le reste de la feature est de la présentation pure (CSS, composants React) : la constitution n'exige pas de tâches de test dédiées, la validation se fait via `quickstart.md` (voir plan.md §Testing — pas de harnais de tests frontend automatisés existant).

**Organization**: Tasks are grouped by user story (US1 → US2 → US3, per spec.md priorities) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths follow the web-app structure from plan.md: `backend/src/`, `backend/tests/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirmer le périmètre d'outillage avant de commencer

- [X] T001 Confirmer qu'aucune nouvelle dépendance n'est nécessaire (research.md Decision 1 et 3) — aucune modification de `frontend/package.json` ni `backend/pyproject.toml` ; Recharts et le CSS natif suffisent

**Checkpoint**: Aucun changement d'outillage requis, on peut passer directement au design system partagé.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Jetons de design et composants partagés dont dépendent les 3 user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Créer `frontend/src/styles/tokens.css` avec la palette de référence du skill data-viz (statut good/warning/serious/critical, rampe séquentielle bleue, surfaces/encre/gridline — research.md Decision 2, data-model.md §2) et l'importer dans `frontend/src/main.tsx`
- [X] T003 [P] Créer le composant `Card.tsx` (surface, padding, bordure cohérents avec `tokens.css`) dans `frontend/src/components/Card.tsx` (depends on T002)
- [X] T004 [P] Créer le composant `StatusBadge.tsx` (badge coloré + icône + label — jamais couleur seule, FR-007) dans `frontend/src/components/StatusBadge.tsx` (depends on T002)

**Checkpoint**: Design system de base prêt — les 3 user stories peuvent commencer.

---

## Phase 3: User Story 1 - Visualiser sa charge d'entraînement d'un coup d'œil (Priority: P1) 🎯 MVP

**Goal**: Le tableau de bord affiche une vraie courbe de tendance de charge dans le temps (pas 2 points isolés), avec un code couleur cohérent pour l'état de charge.

**Independent Test**: quickstart.md §Scénario US1 — vérifier que `GET /api/dashboard/charge` renvoie un champ `historique` à plusieurs points, que le graphique affiche une courbe temporelle, et que l'indicateur/le graphique partagent la même couleur d'état. Testable sans US2/US3.

### Tests for User Story 1

- [X] T005 [US1] Unit test pytest pour `historique_charge()` (paramétrage par date de référence, 8 points hebdomadaires, liste vide si `donnees_suffisantes=false`) dans `backend/tests/unit/test_historique_charge.py` — écrit avant l'implémentation (Principe IV)

### Implementation for User Story 1

- [X] T006 [US1] Backend : paramétrer `calculer_charge()` avec une date de référence optionnelle et ajouter `historique_charge()` dans `backend/src/services/training_load/calcul_charge.py` (depends on T005 ; research.md Decision 4)
- [X] T007 [US1] Backend : étendre `ChargeEntrainementOut` avec `historique: list[PointChargeHistorique]` dans `backend/src/api/schemas.py` (data-model.md §1)
- [X] T008 [US1] Backend : exposer `historique` sur `GET /api/dashboard/charge` dans `backend/src/api/dashboard.py` (depends on T006, T007 ; contracts/dashboard-charge-historique.yaml)
- [X] T009 [P] [US1] Frontend : composant `TrendChart.tsx` (courbe temporelle Recharts, rampe séquentielle bleue de `tokens.css`, tooltip) dans `frontend/src/components/TrendChart.tsx` (depends on T002)
- [X] T010 [P] [US1] Frontend : restyler `ChargeIndicator.tsx` avec `StatusBadge` et les couleurs de statut (normal/surcharge/récupération) dans `frontend/src/components/ChargeIndicator.tsx` (depends on T004)
- [X] T011 [US1] Frontend : intégrer `TrendChart` (remplace le graphique à 2 points) et `ChargeIndicator` restylé dans `frontend/src/pages/Dashboard.tsx` ; restyler le message "données insuffisantes" en `Card` (depends on T008, T009, T010, T003)

**Checkpoint**: User Story 1 fonctionnelle et testable indépendamment (quickstart §US1 passe).

---

## Phase 4: User Story 2 - Explorer visuellement l'historique de mes séances (Priority: P2)

**Goal**: L'historique des séances distingue visuellement l'intensité de chaque séance et rend immédiatement reconnaissables les séances signalées (aberrant/doublon probable), sans changement des données déjà exposées.

**Independent Test**: quickstart.md §Scénario US2 — vérifier l'indication visuelle d'intensité par séance et la reconnaissance immédiate des statuts d'anomalie. Testable indépendamment de US1/US3 (ne nécessite que `GET /api/seances`, déjà fonctionnel).

### Implementation for User Story 2

- [X] T012 [P] [US2] Frontend : composant `SeanceIntensiteBar.tsx` (encodage visuel d'intensité relative par séance, rampe séquentielle de `tokens.css`) dans `frontend/src/components/SeanceIntensiteBar.tsx` (depends on T002)
- [X] T013 [US2] Frontend : restyler `HistoriqueSeances.tsx` — remplacer la table brute par des lignes avec `SeanceIntensiteBar` et `StatusBadge` pour `aberrant`/`doublon_probable` (depends on T012, T004)

**Checkpoint**: User Stories 1 ET 2 fonctionnelles indépendamment.

---

## Phase 5: User Story 3 - Bénéficier d'une identité visuelle cohérente (Priority: P3)

**Goal**: Les 5 pages (dashboard, historique, recommandations, connexions, profil) partagent la même palette, typographie et composants ; les recommandations sont présentées en cartes ; la page active est visuellement mise en évidence.

**Independent Test**: quickstart.md §Scénario US3 — parcourir les 5 pages et vérifier la cohérence visuelle et la mise en évidence de la navigation active.

### Implementation for User Story 3

- [X] T014 [P] [US3] Frontend : restyler `Recommandations.tsx` en cartes `Card` pour chaque recommandation récupération/nutrition (FR-004) dans `frontend/src/pages/Recommandations.tsx` (depends on T003)
- [X] T015 [P] [US3] Frontend : restyler `Connexions.tsx` avec `Card`/`StatusBadge` pour le statut de connexion dans `frontend/src/pages/Connexions.tsx` (depends on T003, T004)
- [X] T016 [P] [US3] Frontend : restyler `Profil.tsx` (formulaire) avec les jetons de `tokens.css` dans `frontend/src/pages/Profil.tsx` (depends on T002)
- [X] T017 [US3] Frontend : mettre en évidence la page active dans la navigation (FR-006) dans `frontend/src/App.tsx` (depends on T002)

**Checkpoint**: Les 3 user stories sont fonctionnelles indépendamment — refonte visuelle complète.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Non-régression et accessibilité, transverses aux 3 user stories

- [X] T018 Rejouer intégralement `specs/001-coaching-velo-garmin-strava/quickstart.md` (US1 → US2 → US3 → export/suppression RGPD) — vérifier zéro régression fonctionnelle (FR-008)
- [X] T019 [P] Revue d'accessibilité : vérifier que chaque usage de couleur d'état (charge, statut de séance, statut de connexion) est accompagné d'un label ou d'une icône, jamais couleur seule (FR-007)
- [X] T020 Run full quickstart.md validation (002) end-to-end (US1 → US2 → US3)

**Checkpoint**: Feature complete, sans régression, conforme au Principe IV et à FR-007/FR-008.

> **Note on T018/T020** : validé avec une base PostgreSQL 16 réelle (`coaching-db`, dev) + une base de test isolée (`coaching_test`, port 5543, supprimée après usage). Suite pytest complète : 33 tests passés (30 de la feature 001 + 3 nouveaux pour `historique_charge`, T005). Backend (`uvicorn`) et frontend (`vite`) lancés en conditions réelles ; données seedées directement en base (profil athlète + ~40 séances sur 10 semaines, incluant une séance `aberrant` et un `doublon_probable`) puis purgées après validation. Les 5 pages ont été capturées via Chromium headless (Playwright, installé temporairement pour cette vérification) : `GET /api/dashboard/charge` renvoie bien un `historique` à 8 points réels (au lieu de 2), le tableau de bord affiche la courbe temporelle et le badge d'état coloré, l'historique des séances affiche la barre d'intensité et les badges d'anomalie, les recommandations sont rendues en cartes formatées (calories/macros, intensité du lendemain — plus de dump JSON brut), Connexions/Profil sont visuellement cohérents avec le reste, et la page active est mise en évidence dans la navigation. Zéro erreur console sur les 5 pages.
>
> **Constat hors périmètre de cette feature** (à traiter séparément, cf. instruction CLAUDE.md de signaler les problèmes plutôt que les corriger silencieusement) : le job périodique `generer_pour_nouvelles_seances` (`backend/src/jobs/generer_recommandations.py`, feature 001) génère une paire de recommandations par séance sans historique de recommandation, sans plafond. Un import initial ou un seed en masse (comme lors de cette validation) produit donc des dizaines de cartes de recommandation quasi identiques sur la page Recommandations. Comportement inchangé par cette feature (FR-008 respecté), mais c'est un défaut préexistant de la feature 001 qui dégrade l'expérience visuelle qu'on vient d'améliorer.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational only. No dependency on US2/US3.
- **User Story 2 (Phase 4)**: Depends on Foundational only. Indépendante de US1/US3 — consomme uniquement `GET /api/seances`, déjà fonctionnel.
- **User Story 3 (Phase 5)**: Depends on Foundational only. Complète l'expérience une fois US1/US2 livrées, mais reste testable seule (spec.md).
- **Polish (Phase 6)**: Depends on all three user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependencies on other stories — MVP entry point de cette feature.
- **US2 (P2)**: Fonctionnellement indépendante — aucun changement backend requis.
- **US3 (P3)**: Fonctionnellement indépendante — dépend uniquement des composants Foundational (`Card`, `tokens.css`), pas du travail de US1/US2.

### Within Each User Story

- Tests before implementation pour la seule logique d'analyse (T005 avant T006 — Principe IV).
- Composants avant intégration dans les pages.
- Story complete et checkpoint validé avant de passer à la story suivante.

### Parallel Opportunities

- Toutes les tâches Foundational marquées [P] (T002-T004) — T003/T004 dépendent de T002 mais sont parallélisables entre elles une fois T002 fait.
- Une fois Foundational terminé, US1, US2, US3 peuvent avancer en parallèle par différents développeurs.
- Au sein de US1 : T009 (TrendChart) et T010 (ChargeIndicator) sont indépendants (fichiers différents), T011 les intègre ensuite.
- Au sein de US3 : T014, T015, T016 (pages différentes) sont pleinement parallélisables ; T017 (navigation) est indépendant des 3.

---

## Parallel Example: User Story 3

```bash
# Les 3 pages restylées en parallèle (fichiers différents) :
Task: "Restyler Recommandations.tsx en cartes dans frontend/src/pages/Recommandations.tsx"
Task: "Restyler Connexions.tsx avec Card/StatusBadge dans frontend/src/pages/Connexions.tsx"
Task: "Restyler Profil.tsx avec les jetons de tokens.css dans frontend/src/pages/Profil.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (bloque toutes les stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: quickstart.md §US1 indépendamment
5. Demo : tableau de bord avec vraie courbe de tendance de charge

### Incremental Delivery

1. Setup + Foundational → design system prêt
2. Add US1 → valider via quickstart §US1 → demo (MVP visuel)
3. Add US2 → valider via quickstart §US2 → demo (historique coloré)
4. Add US3 → valider via quickstart §US3 → demo (cohérence sur les 5 pages)
5. Polish (non-régression 001, accessibilité) → valider `quickstart.md` (002) complet

### Parallel Team Strategy

Avec plusieurs développeurs, une fois Foundational terminé :

- Développeur A : US1 (extension backend + Dashboard)
- Développeur B : US2 (HistoriqueSeances) — n'a besoin que de `GET /api/seances`, déjà fonctionnel
- Développeur C : US3 (Recommandations, Connexions, Profil, navigation)

---

## Notes

- [P] tasks = fichiers différents, pas de dépendance.
- [Story] label mappe chaque tâche à sa user story pour la traçabilité.
- Tests inclus uniquement là où la constitution les exige (logique d'analyse — Principe IV) ; le reste est validé visuellement via quickstart.md.
- Commit après chaque tâche ou groupe logique.
- S'arrêter à chaque checkpoint pour valider une story indépendamment avant de continuer.
