# Quickstart : Refonte visuelle de l'application

**Feature**: `002-améliore-design-application` | **Date**: 2026-08-15

Scénarios de validation visuelle pour chaque user story, dans l'ordre de priorité (US1 → US2 → US3), conformément au Principe III (MVP incrémental). Cette feature est purement visuelle (FR-008) : chaque scénario vérifie l'absence de régression fonctionnelle en plus du résultat visuel.

## Prérequis

Identiques à `specs/001-coaching-velo-garmin-strava/quickstart.md` (backend + frontend démarrés, base PostgreSQL migrée). Un historique de séances d'au moins 4 à 8 semaines est nécessaire pour valider pleinement US1 (courbe de tendance) — le seeder/les fixtures de test de 001 peuvent être réutilisés.

## Scénario US1 — Visualiser sa charge d'entraînement d'un coup d'œil (P1)

**Correspond à**: spec.md Acceptance Scenarios 1-3 de US1, SC-001, SC-002.

1. Ouvrir le tableau de bord avec un historique de séances sur au moins 4 semaines.
2. **Vérifier** : `GET /api/dashboard/charge` renvoie un champ `historique` avec plusieurs points hebdomadaires (pas seulement 2 valeurs isolées).
3. **Vérifier** : le graphique affiche une courbe temporelle (plusieurs points dans le temps), pas une comparaison à 2 barres/points.
4. **Vérifier** : l'indicateur de charge et le graphique utilisent la même couleur pour un même état (normal/surcharge/récupération) — comparer visuellement les deux.
5. Réduire l'historique de test à moins de 2 semaines.
6. **Vérifier** : le message "données insuffisantes" est présenté avec la même mise en forme visuelle que le reste de la page (carte/bandeau stylé), pas un `<p>` brut.

*Testable indépendamment de US2/US3 — aucune page autre que le tableau de bord n'est requise.*

## Scénario US2 — Explorer visuellement l'historique de mes séances (P2)

**Correspond à**: spec.md Acceptance Scenarios 1-3 de US2.

1. Ouvrir l'historique avec des séances d'intensités variées (courtes/longues, légères/intenses) et au moins une séance marquée `aberrant` ou `doublon_probable`.
2. **Vérifier** : chaque séance porte une indication visuelle (couleur) reflétant son intensité relative.
3. **Vérifier** : la séance marquée `aberrant`/`doublon_probable` reste identifiable au premier coup d'œil (badge/couleur), pas seulement un texte en petit.
4. Faire défiler une longue liste de séances.
5. **Vérifier** : la lecture reste confortable (espacement, alternance visuelle), aucune régression sur les données affichées (date, durée, distance, puissance, FC, dénivelé restent toutes présentes et exactes).

*Testable indépendamment de US1/US3 — nécessite uniquement `GET /api/seances`, déjà fonctionnel.*

## Scénario US3 — Bénéficier d'une identité visuelle cohérente (P3)

**Correspond à**: spec.md Acceptance Scenarios 1-3 de US3.

1. Parcourir les 5 pages (tableau de bord, historique, recommandations, connexions, profil).
2. **Vérifier** : palette de couleurs, typographie et composants (cartes, badges, boutons) identiques d'une page à l'autre.
3. Ouvrir la page Recommandations avec au moins une recommandation de récupération et une estimation nutritionnelle.
4. **Vérifier** : chaque recommandation est présentée en carte visuelle distincte (pas en texte brut), cohérente avec le reste de l'application.
5. Naviguer d'une page à l'autre via le menu.
6. **Vérifier** : la page active est visuellement mise en évidence dans la navigation.

*Complète l'expérience une fois US1/US2 livrées — dépend d'elles pour ne pas laisser le tableau de bord et l'historique comme îlots visuels incohérents avec le reste.*

## Vérification de non-régression (FR-008)

Après les 3 scénarios ci-dessus, rejouer intégralement `specs/001-coaching-velo-garmin-strava/quickstart.md` (US1 → US2 → US3 → export/suppression RGPD) : tous les comportements fonctionnels doivent rester identiques à ceux validés lors de la feature 001 — seule la présentation change.
