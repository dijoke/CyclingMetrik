# Implementation Plan: Restructuration du design (mode sombre, navigation, vue d'ensemble)

**Branch**: `006-restructuration-design-mode` | **Date**: 2026-08-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-restructuration-design-mode/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Modernisation visuelle en trois volets, tous frontend-only : mode sombre (bascule explicite + suivi système, valeurs reprises de la palette de référence déjà validée du skill data-viz — research.md Decision 1/2), remplacement de la sidebar par une navigation horizontale (Decision 4), et un aperçu "tuiles KPI" en haut du tableau de bord composant des données déjà exposées par les endpoints existants (Decision 5, zéro nouvel endpoint). Aucune nouvelle dépendance, aucun changement de comportement fonctionnel (FR-008).

## Technical Context

**Language/Version**: TypeScript 5.x / React 18 (frontend uniquement — aucun changement backend)

**Primary Dependencies**: Aucune nouvelle dépendance — CSS natif (extension de `tokens.css`), React state + `localStorage` pour la préférence de thème, `react-router-dom` déjà en place pour la navigation

**Storage**: Inchangé — la préférence de thème vit dans `localStorage` du navigateur, pas en base de données (data-model.md)

**Testing**: Validation visuelle/manuelle via `quickstart.md`, cohérente avec l'approche déjà utilisée pour les features 002/004/005 (pas de logique d'analyse introduite ici — Principe IV non applicable, uniquement présentation/navigation)

**Target Platform**: Web — inchangé

**Project Type**: web (frontend uniquement pour cette feature)

**Performance Goals**: SC-001 — bascule de thème instantanée (pas de rechargement) ; SC-003 — état global visible en < 5s de consultation du tableau de bord

**Constraints**: FR-004 — contraste suffisant sur les 6 pages en thème sombre ; FR-008 — zéro changement de comportement fonctionnel ; FR-007 — absence de donnée explicite plutôt que valeur trompeuse dans les tuiles KPI

**Scale/Scope**: 3 user stories P1→P2→P3, extension de `tokens.css`, restructuration de `App.tsx`, extension de `Dashboard.tsx`, nouveau composant de bascule de thème

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Justification |
|---|---|---|
| I. Athlete Safety Over Cleverness (NON-NEGOTIABLE) | ✅ PASS | Aucune recommandation modifiée. FR-007 applique l'esprit du principe aux tuiles KPI : jamais de valeur affichée sans donnée pour la fonder. |
| II. Data-First & Privacy by Design | ✅ PASS | La préférence de thème n'est pas une donnée de santé/entraînement ; stockée localement navigateur, jamais transmise au serveur. |
| III. MVP Incrémental par User Story | ✅ PASS | US1 (thème) → US2 (navigation) → US3 (vue d'ensemble) indépendamment livrables et testables. |
| IV. Test-First sur la logique d'analyse | N/A | Aucune nouvelle logique de calcul — uniquement présentation, navigation et composition d'affichage de données déjà calculées ailleurs (specs 001/004/005, déjà testées à leur source). |
| V. Simplicité & Dette Justifiée | ✅ PASS | Pas de bibliothèque de thématisation tierce (Decision 1) ; paires de couleurs de graphiques dérivées de valeurs déjà publiées plutôt qu'une nouvelle rampe validée séparément (Decision 2) ; zéro nouvel endpoint pour la vue d'ensemble (Decision 5). |

Aucune violation nécessitant la section Complexity Tracking.

**Re-check post-Phase 1** : data-model.md confirme qu'aucune entité ni endpoint n'est ajouté ; la vue d'ensemble compose exclusivement des champs déjà exposés. Les gates restent stables.

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
frontend/
├── src/
│   ├── styles/tokens.css              # étendu : valeurs sombres (research.md Decision 1)
│   ├── hooks/useTheme.ts              # nouveau : lecture/écriture du thème (localStorage + prefers-color-scheme)
│   ├── components/
│   │   ├── ThemeToggle.tsx            # nouveau : contrôle de bascule clair/sombre
│   │   ├── TrendChart.tsx             # étendu : paires de couleurs clair/dark (Decision 2)
│   │   └── VolumeBarChart.tsx         # étendu : paires de couleurs clair/dark (Decision 2)
│   ├── pages/Dashboard.tsx            # étendu : tuiles KPI en haut de page (US3)
│   └── App.tsx                        # restructuré : navigation top-bar (US2) + intégration ThemeToggle

backend/   # non modifié par cette feature
```

**Structure Decision**: Structure inchangée (`backend/`, `frontend/`) — feature strictement frontend. Nouveau dossier `hooks/` (absent jusqu'ici) pour isoler la logique de thème du composant de bascule, cohérent avec la séparation déjà en place entre `components/`, `pages/`, `services/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
