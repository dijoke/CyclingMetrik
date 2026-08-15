# Data Model: Restructuration du design (mode sombre, navigation, vue d'ensemble)

**Feature**: `006-restructuration-design-mode` | **Date**: 2026-08-15

Aucune nouvelle entité métier, aucun changement de schéma, aucun nouvel endpoint (research.md Decision 5). Cette feature ajoute uniquement :

1. **Préférence d'affichage (frontend uniquement, non persistée côté serveur)** : `theme: "light" | "dark"`, stockée dans `localStorage` du navigateur — ce n'est pas une donnée métier liée à l'athlète, elle n'a pas vocation à être synchronisée entre appareils.
2. **Jetons de design sombres** (CSS, `tokens.css`) — extension des jetons clairs déjà définis en spec 002, voir research.md Decision 1/2.

## Composition de la vue d'ensemble (US3)

Aucune nouvelle donnée : les tuiles KPI du tableau de bord composent à l'affichage des champs déjà renvoyés par des endpoints existants :

| Tuile | Source | Champ(s) |
|---|---|---|
| État de charge | `GET /api/dashboard/charge` | `tendance`, `ratio_acwr`, `donnees_suffisantes` |
| Volume année en cours | `GET /api/statistiques/comparaison-annuelle` | `annee_courante.distance_metres`, `annee_courante.nb_seances` |
| Record marquant | `GET /api/statistiques/records` | `plus_longue_distance` (ou équivalent, `null` géré explicitement — FR-007) |
