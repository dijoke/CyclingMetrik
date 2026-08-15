# Implementation Plan: Historique des séances enrichi (filtres, détail, records de puissance)

**Branch**: `007-historique-des-séances` | **Date**: 2026-08-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-historique-des-séances/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Trois volets : tri/filtre client sur l'historique existant (US1), page de détail par séance via un nouvel endpoint `GET /api/seances/{id}` (US2), et records de puissance par durée calculés depuis le flux Strava "streams" (US3), stockés dans 5 nouvelles colonnes nullable et rétro-remplis sur l'historique complet (787 séances) par un job de fond borné par les limites de débit déjà gérées (feature 004). Aucun changement de comportement existant (FR-009).

## Technical Context

**Language/Version**: Python 3.12 (backend : migration, nouveau job, nouvel endpoint) ; TypeScript 5.x / React 18 (frontend : tri/filtre, page de détail)

**Primary Dependencies**: Aucune nouvelle dépendance — `httpx` (déjà présent) pour l'appel au flux Strava, SQLAlchemy/Alembic pour la migration, `react-router-dom` (déjà présent) pour la route de détail

**Storage**: PostgreSQL — nouvelle migration Alembic (6 colonnes nullable sur `seance`, data-model.md) ; pas de nouvelle table

**Testing**: pytest — la fonction de calcul de records (liste de watts → 5 valeurs, research.md Decision 3) est pure et testée en premier (Principe IV) ; le tri/filtre frontend est validé via `quickstart.md` (présentation, pas de logique d'analyse)

**Target Platform**: Web — inchangé

**Project Type**: web (frontend + backend)

**Performance Goals**: SC-001 — retrouver une séance en < 15s via tri/filtre ; SC-002 — 100% des séances avec puissance moyenne traitées (résultat ou constat d'absence) dans les jours suivant le déploiement, backfill de 787 séances borné par le débit Strava (plusieurs heures, accepté — spec.md Assumptions)

**Constraints**: FR-007/FR-008 — le backfill ne bloque rien et ne retente pas indéfiniment ; FR-006 — absence de record jamais confondue avec zéro ; FR-009 — zéro régression sur l'import/déduplication/statuts existants

**Scale/Scope**: 1 migration (6 colonnes), 1 nouveau job de fond, 1 nouvel endpoint, extension d'un schéma existant, 1 nouvelle page frontend, tri/filtre sur la page existante — 3 user stories P1→P2→P3

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Justification |
|---|---|---|
| I. Athlete Safety Over Cleverness (NON-NEGOTIABLE) | ✅ PASS | Aucune recommandation modifiée. FR-006 applique l'esprit du principe aux records de puissance : jamais de valeur affichée sans donnée pour la fonder. |
| II. Data-First & Privacy by Design | ✅ PASS | Le flux de puissance brut n'est pas conservé (research.md Decision 3) — seules 5 valeurs dérivées sont stockées, réduisant la surface de données sensibles plutôt que l'augmentant. |
| III. MVP Incrémental par User Story | ✅ PASS | US1 (tri/filtre) → US2 (détail) → US3 (records) indépendamment livrables ; US3 la plus coûteuse est aussi la moins prioritaire. |
| IV. Test-First sur la logique d'analyse | ✅ PASS | La fonction de calcul de meilleure moyenne glissante est pure et testée avant implémentation (research.md Decision 3). |
| V. Simplicité & Dette Justifiée | ✅ PASS | Pas de nouvelle dépendance (pas de file de tâches dédiée, réutilisation d'APScheduler — Decision 4) ; pas de stockage du flux brut (Decision 3) ; tri/filtre client plutôt que nouveaux paramètres d'API (Decision 1). |

Aucune violation nécessitant la section Complexity Tracking.

**Re-check post-Phase 1** : data-model.md confirme que l'extension reste additive (6 colonnes nullable, aucune migration destructive) et que le contrat (`contracts/api-seance-detail.yaml`) n'altère aucun endpoint existant dans son comportement actuel. Les 5 gates restent au vert.

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
├── alembic/versions/xxxx_ajout_records_puissance.py   # nouveau : 6 colonnes nullable sur seance
├── src/
│   ├── models/seance.py                               # étendu : 6 nouvelles colonnes
│   ├── integrations/strava/connecteur.py               # étendu : recuperer_flux_puissance()
│   ├── services/puissance/records.py                   # nouveau : calculer_records_puissance() (fonction pure)
│   ├── jobs/calculer_records_puissance.py               # nouveau : job de fond (backfill + nouvelles séances)
│   ├── api/schemas.py                                   # étendu : SeanceOut + 5 champs
│   ├── api/seances.py                                   # étendu : GET /api/seances/{id}
│   └── main.py                                          # étendu : enregistrement du nouveau job
└── tests/unit/test_records_puissance.py                  # nouveau : tests avant implémentation (Principe IV)

frontend/
├── src/
│   ├── pages/
│   │   ├── HistoriqueSeances.tsx    # étendu : tri/filtre, lignes cliquables
│   │   └── SeanceDetail.tsx         # nouvelle page (route /seances/:id)
│   ├── services/api_client.ts       # étendu : Seance + puissance_max_*, seances.detail()
│   └── App.tsx                      # étendu : route /seances/:id
```

**Structure Decision**: Structure inchangée (`backend/`, `frontend/`). Nouveau module de service backend isolé (`services/puissance/`), suivant le même patron que `services/statistiques/` (spec 005) et `services/training_load/` (spec 001) — fonction de calcul pure et testée, séparée de l'intégration réseau (connecteur) et de la planification (job).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
