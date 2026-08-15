# Implementation Plan: Import complet de l'historique Strava et conservation illimitée

**Branch**: `004-importer-intégralité-historique` | **Date**: 2026-08-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-importer-intégralité-historique/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Le connecteur Strava importe aujourd'hui au maximum 100 activités des 30 derniers jours (un seul appel API, sans pagination). Cette feature fait paginer `StravaConnecteur.recuperer_seances` sur l'intégralité de l'historique disponible lors de la première connexion (FR-001/FR-002), gère les limites de débit Strava par un retry borné plutôt qu'un échec silencieux (FR-003), et retire le job de purge automatique à 3 mois pour une conservation illimitée (FR-004). Aucun nouveau modèle de données, aucun nouvel endpoint : changements confinés au connecteur Strava, à `import_seances.py` (borne temporelle de la première synchronisation) et à la suppression du job `purge_retention`.

## Technical Context

**Language/Version**: Python 3.12 (backend uniquement — aucun changement frontend)

**Primary Dependencies**: Aucune nouvelle dépendance — `httpx` (déjà présent) et `time.sleep` de la stdlib suffisent pour la pagination et le backoff de retry

**Storage**: Inchangé (PostgreSQL) — aucune nouvelle colonne/table ; le retrait du job de purge ne change aucun schéma

**Testing**: pytest — tests de contrat étendus pour `StravaConnecteur.recuperer_seances` (pagination multi-pages, retry sur 429) avant l'implémentation (Principe IV : la logique d'import/pagination est une intégration externe couverte par les tests de contrat existants)

**Target Platform**: Web — backend uniquement, inchangé

**Project Type**: web (frontend + backend, mais cette feature ne touche que le backend)

**Performance Goals**: SC-001 (100% des activités Strava importées) ; SC-003 (import > 100 activités réussi même avec limite de débit temporaire) — pas d'exigence de latence stricte, un import initial volumineux peut prendre plusieurs minutes (borné par le backoff de retry, research.md Decision 3)

**Constraints**: FR-003 — pas d'échec silencieux/partiel sur limite de débit ; aucune régression sur Garmin/Nolio (non modifiés, research.md Decision 2) ; FR-005 — l'export/suppression RGPD (spec 001 FR-013) doit continuer de fonctionner à l'identique

**Scale/Scope**: 1 connecteur modifié (Strava), 1 fichier de service modifié (`import_seances.py`), 1 job supprimé (`purge_retention.py`), 2 user stories P1→P2

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Justification |
|---|---|---|
| I. Athlete Safety Over Cleverness (NON-NEGOTIABLE) | ✅ PASS | Aucun changement à la logique de recommandation ou de charge. Un historique plus long ne modifie que les données d'entrée, pas les règles d'analyse. |
| II. Data-First & Privacy by Design | ⚠️ Changement assumé | Le retrait de la purge automatique (FR-004) s'écarte de la rétention de 3 mois décidée dans la spec 001. Choix explicite et confirmé par l'utilisateur (voir spec.md, Assumptions) ; le droit à l'export/suppression (FR-013, Principe II) reste pleinement garanti — seule la suppression *automatique et non consentie* est retirée, pas le contrôle de l'athlète sur ses données. |
| III. MVP Incrémental par User Story | ✅ PASS | US1 (import complet) et US2 (conservation illimitée) sont indépendamment testables, US1 en priorité car US2 n'a de valeur réelle qu'une fois l'historique complet disponible. |
| IV. Test-First sur la logique d'analyse | ✅ PASS | La pagination et le retry sur limite de débit sont testés en premier via des tests de contrat étendus (`test_strava_connecteur.py`), avant modification du connecteur. |
| V. Simplicité & Dette Justifiée | ✅ PASS | Aucune nouvelle dépendance (pas de file de tâches, pas de tracking de reprise dédié) — la ré-exécution idempotente déjà garantie par la contrainte d'unicité `id_externe` sert de mécanisme de reprise (research.md Decision 3). Le job de purge est supprimé plutôt que désactivé par un flag (Decision 4). |

**Note sur le Principe II** : ce n'est pas une violation à corriger, mais un changement de politique produit explicitement demandé et confirmé par l'utilisateur — documenté ici pour traçabilité plutôt que caché.

**Re-check post-Phase 1** : data-model.md confirme qu'aucune entité n'est ajoutée et que le retrait du job de purge ne touche aucun schéma. Les 5 gates restent stables ; le point Principe II reste un changement de politique assumé, pas une violation non traitée.

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
│   ├── integrations/strava/connecteur.py   # étendu : pagination + retry sur limite de débit
│   ├── services/import_seances.py          # étendu : depuis=None pour la 1ère sync Strava
│   ├── jobs/purge_retention.py             # supprimé
│   └── main.py                              # étendu : retrait de l'enregistrement du job de purge
└── tests/contract/test_strava_connecteur.py  # étendu : pagination multi-pages, retry 429

frontend/   # non modifié par cette feature
```

**Structure Decision**: Structure inchangée par rapport aux features 001/002 (`backend/`, `frontend/`). Cette feature est backend-only et confinée à l'intégration Strava et à la planification des jobs — aucun nouveau module.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
