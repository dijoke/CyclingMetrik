# Implementation Plan: Refonte visuelle de l'application

**Branch**: `002-améliore-design-application` | **Date**: 2026-08-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-améliore-design-application/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Refonte purement visuelle de l'application (aucun changement fonctionnel, FR-008) : le tableau de bord passe d'un graphique à 2 points à une vraie courbe de tendance de charge sur plusieurs semaines (US1), l'historique des séances gagne un code couleur d'intensité et des statuts d'anomalie visibles au premier coup d'œil (US2), et les 5 pages partagent une identité visuelle cohérente — palette, typographie, cartes/badges (US3). Approche technique : réutilisation de la palette de référence déjà validée du skill data-viz interne (accessibilité daltonisme acquise sans travail de validation supplémentaire), CSS natif (variables + classes de composants) plutôt qu'un framework, extension de Recharts déjà en place (aucune nouvelle dépendance JS), et une petite extension backend pour exposer une vraie série temporelle de charge sans dupliquer la logique d'analyse côté frontend (Principe IV).

## Technical Context

**Language/Version**: TypeScript 5.x / React 18 (frontend, inchangé) ; Python 3.12 (backend, extension ciblée du endpoint dashboard existant)

**Primary Dependencies**: Aucune nouvelle dépendance. Recharts (déjà présent) étendu pour la courbe temporelle et le graphique d'historique de séances ; CSS natif avec variables custom properties pour les jetons de design (pas de Tailwind/MUI/styled-components — voir research.md Decision 1)

**Storage**: Inchangé (PostgreSQL 15+) — aucune nouvelle entité persistée (voir data-model.md) ; l'historique de charge est calculé à la volée, non stocké

**Testing**: pytest pour la nouvelle logique de série temporelle de charge côté backend, écrite avant l'implémentation (Principe IV — c'est de la logique d'analyse) ; validation visuelle/manuelle via `quickstart.md` pour le frontend, cohérente avec la méthode déjà utilisée pour valider le Polish de la feature 001 (pas de harnais de tests automatisés frontend existant à ce jour)

**Target Platform**: Web — inchangé

**Project Type**: web (frontend + backend, structure inchangée de la feature 001)

**Performance Goals**: SC-001 — identifier l'état de charge en moins de 5 secondes de consultation (amélioration du SC-003 de la feature 001, qui était de 10s) ; le nouveau champ `historique` ne doit pas dégrader le temps de réponse perçu du tableau de bord (calcul backend sur des fenêtres déjà indexées par date de séance)

**Constraints**: FR-008 — zéro régression fonctionnelle, changement strictement visuel ; FR-007 — distinction daltonisme sur les couleurs d'état (satisfait par réutilisation de la palette de référence validée) ; Principe V — aucune nouvelle dépendance non justifiée

**Scale/Scope**: 5 pages restylées (Dashboard, HistoriqueSeances, Recommandations, Connexions, Profil) ; 1 endpoint backend étendu (`GET /api/dashboard/charge`) ; 3 user stories P1→P2→P3 indépendamment livrables

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Justification |
|---|---|---|
| I. Athlete Safety Over Cleverness (NON-NEGOTIABLE) | ✅ PASS | Aucun changement à la logique de recommandation (toujours rule-based, toujours gatée sur `donnees_suffisantes`). Le message "données insuffisantes" est mieux mis en valeur visuellement, pas modifié dans sa condition d'affichage. |
| II. Data-First & Privacy by Design | ✅ PASS | Aucune nouvelle donnée collectée, aucun nouveau champ tiers stocké. Le champ `historique` agrège des séances déjà scopées à l'athlète authentifié, calculé à la volée (non persisté). |
| III. MVP Incrémental par User Story | ✅ PASS | US1 (tableau de bord) → US2 (historique) → US3 (cohérence globale) sont chacune indépendamment testables et livrables, dans cet ordre de priorité, sans dépendance bloquante inverse. |
| IV. Test-First sur la logique d'analyse | ✅ PASS (avec exigence explicite) | La nouvelle fonction de série temporelle de charge (extension de `calculer_charge`) EST de la logique d'analyse : un test pytest DOIT être écrit avant son implémentation, comme pour le reste du moteur de charge (feature 001). Le reste de la feature (CSS, composants React) est hors du périmètre du Principe IV (présentation, pas analyse). |
| V. Simplicité & Dette Justifiée | ✅ PASS | Aucune nouvelle dépendance : Recharts déjà présent, CSS natif plutôt qu'un framework (research.md Decision 1), palette déjà validée plutôt que ré-inventée (Decision 2). |

Aucune violation nécessitant la section Complexity Tracking.

**Re-check post-Phase 1** : data-model.md confirme qu'aucune entité persistée n'est ajoutée (Principe II) et que l'unique extension (`historique` sur `ChargeEntrainementOut`) est un champ dérivé, calculé, non stocké. Le contrat (`contracts/dashboard-charge-historique.yaml`) documente cette extension comme strictement additive sur l'endpoint existant — aucun contrat de la feature 001 n'est modifié dans son comportement actuel, confirmant FR-008. Les 5 gates restent au vert sans nouvelle violation.

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
│   ├── services/training_load/calcul_charge.py   # étendu : paramétrer par date de référence, fonction historique_charge()
│   └── api/dashboard.py                          # étendu : champ `historique` sur GET /api/dashboard/charge
└── tests/unit/                                    # nouveau test pytest pour historique_charge() (Principe IV, avant impl.)

frontend/
├── src/
│   ├── styles/
│   │   └── tokens.css        # nouveau : variables CSS (palette, typographie, surfaces — research.md Decision 1/2)
│   ├── components/
│   │   ├── ChargeIndicator.tsx     # restylé (existant)
│   │   ├── TrendChart.tsx          # nouveau : courbe temporelle de charge (US1)
│   │   ├── StatusBadge.tsx         # nouveau : badge coloré réutilisable (états de charge, statuts de séance)
│   │   ├── Card.tsx                # nouveau : carte réutilisable (recommandations, séances, statuts)
│   │   └── SeanceIntensiteBar.tsx  # nouveau : encodage visuel d'intensité (US2)
│   ├── pages/                # Dashboard, HistoriqueSeances, Recommandations, Connexions, Profil — restylées, pas de nouvelle page
│   └── App.tsx                # navigation restylée (page active mise en évidence, US3 FR-006)
└── tests/                    # aucun harnais existant (voir Testing ci-dessus) — validation via quickstart.md
```

**Structure Decision**: Structure inchangée par rapport à la feature 001 (deux projets séparés `backend/`, `frontend/`). Cette feature n'ajoute aucun nouveau module de premier niveau : elle étend un service et un endpoint backend existants, et ajoute des composants de présentation + une feuille de jetons CSS côté frontend, conformément à son périmètre strictement visuel (FR-008).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
