# Implementation Plan: Coaching vélo connecté (import séances + conseils récupération/nutrition)

**Branch**: `001-coaching-velo-garmin-strava` | **Date**: 2026-08-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-coaching-velo-garmin-strava/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Application web où un athlète cycliste connecte Garmin Connect, Strava et/ou Nolio pour importer automatiquement ses séances (US1), consulte un tableau de bord de charge d'entraînement avec détection de surcharge (US2), et reçoit des recommandations de récupération et de nutrition explicables, jamais affichées sans données suffisantes (US3, Principe I de la constitution). Approche technique : backend Python/FastAPI exposant une API REST, stockage PostgreSQL, connecteurs OAuth par plateforme avec synchronisation planifiée, moteur de charge et de recommandations basé sur des règles explicites (pas de boîte noire ML) pour rester conforme au Principe I, frontend React/TypeScript pour le tableau de bord.

## Technical Context

**Language/Version**: Python 3.12 (backend) ; TypeScript 5.x / Node.js 20 (frontend)

**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 + Alembic (migrations), httpx (appels OAuth/API Garmin/Strava/Nolio), APScheduler (jobs planifiés : sync périodique, purge de rétention) ; React 18 + Vite, Recharts (graphiques de charge d'entraînement), React Query (état serveur)

**Storage**: PostgreSQL 15+ (séances, profils athlètes, connexions plateformes, recommandations) ; tokens OAuth chiffrés at-rest (colonne chiffrée via `cryptography`/Fernet, jamais en clair — Principe II)

**Testing**: pytest + pytest-asyncio (unit + intégration backend), tests de contrat par plateforme source (Garmin/Strava/Nolio, avec fixtures rejouables pour détecter les changements de format d'API) ; Vitest + React Testing Library (frontend)

**Target Platform**: Web — backend déployé sur serveur Linux (conteneur), frontend SPA servie au navigateur

**Project Type**: web (frontend + backend détectés)

**Performance Goals**: import initial ≤ 5 min (SC-001) ; 95% des séances synchronisées sous 24h (SC-002) ; lecture de l'état de charge en < 10s de consultation du dashboard (SC-003, guidé par le design plutôt que la perf brute) ; recommandation disponible ≤ 2 min après import d'une séance significative (SC-005)

**Constraints**: aucun identifiant de plateforme tierce en clair (Principe II) ; rétention des séances = 3 mois glissants avec purge automatique (FR-012) ; export/suppression des données conforme RGPD, France/UE uniquement (FR-013) ; aucune recommandation affichée sans données suffisantes (FR-011, Principe I, NON-NEGOTIABLE)

**Scale/Scope**: mono-athlète par compte (pas de multi-athlète/coach en v1) ; 3 intégrations externes (Garmin Connect, Strava, Nolio) ; 3 user stories MVP (import, analyse de charge, recommandations)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Justification |
|---|---|---|
| I. Athlete Safety Over Cleverness (NON-NEGOTIABLE) | ✅ PASS | Le moteur de recommandations est rule-based et explicable (pas de ML boîte noire). L'entité `Recommandation` porte toujours sa justification (données sources). Un état explicite "données insuffisantes" est modélisé plutôt qu'une valeur par défaut silencieuse (FR-011). |
| II. Data-First & Privacy by Design | ✅ PASS | OAuth standard par plateforme, tokens chiffrés en base (jamais en clair). Endpoints d'export et de suppression des données prévus dès Phase 1 (contracts/). Purge automatique à 3 mois (FR-012). |
| III. MVP Incrémental par User Story | ✅ PASS | Structure backend en modules par domaine (import, charge, recommandations) permettant de livrer et démontrer US1 avant US2 avant US3, sans dépendance bloquante inverse. |
| IV. Test-First sur la logique d'analyse | ✅ PASS | pytest requis avant implémentation pour le calcul de charge et la génération de recommandations ; tests de contrat par plateforme source pour détecter les dérives de format d'API. |
| V. Simplicité & Dette Justifiée | ✅ PASS | APScheduler in-process choisi plutôt que Celery+Redis pour la synchronisation planifiée (échelle mono-athlète v1) — voir research.md pour l'alternative écartée. Aucune abstraction supplémentaire non justifiée. |

Aucune violation nécessitant la section Complexity Tracking.

**Re-check post-Phase 1** : la conception détaillée (data-model.md, contracts/) confirme les 5 gates sans introduire de nouvelle violation — en particulier, l'entité `Recommandation` impose par construction l'invariant "pas de contenu sans justification, pas de statut disponible sans données suffisantes" (Principe I), et `contracts/api.openapi.yaml` expose les endpoints d'export/suppression RGPD dès la conception (Principe II).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # Athlete, Séance, ChargeEntrainement, Recommandation, ConnexionPlateforme
│   ├── integrations/     # connecteurs Garmin Connect / Strava / Nolio (OAuth + import + webhooks/polling)
│   ├── services/
│   │   ├── training_load/   # calcul de charge, tendance, détection de surcharge (US2)
│   │   └── recommendations/ # règles de récupération + nutrition, garde-fou "données insuffisantes" (US3)
│   ├── api/               # routes FastAPI (séances, dashboard, profil, connexions, export/suppression RGPD)
│   └── jobs/              # APScheduler : sync périodique par plateforme, purge de rétention à 3 mois
└── tests/
    ├── contract/           # fixtures rejouables par plateforme source (Garmin/Strava/Nolio)
    ├── integration/        # scénarios bout-en-bout par user story (US1/US2/US3)
    └── unit/               # calcul de charge, moteur de recommandations (test-first, Principe IV)

frontend/
├── src/
│   ├── components/         # graphiques de charge, cartes de recommandation, badges de statut connexion
│   ├── pages/               # Historique séances, Dashboard charge, Recommandations, Profil athlète
│   └── services/            # client API, gestion état serveur (React Query)
└── tests/
```

**Structure Decision**: Application web à deux projets séparés (`backend/`, `frontend/`) — Option 2 du template, car la feature nécessite explicitement une API backend (intégrations OAuth, calculs, planification) et une interface web interactive (tableau de bord). Le backend est lui-même organisé par domaine métier (`integrations/`, `training_load/`, `recommendations/`) pour que chaque user story (US1 → US2 → US3) soit livrable indépendamment, conformément au Principe III.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
