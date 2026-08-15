# Data Model: Refonte visuelle de l'application

**Feature**: `002-améliore-design-application` | **Date**: 2026-08-15

Aucune nouvelle entité persistée (base de données inchangée) — conforme à FR-008 et à la section Key Entities de `spec.md`. Cette feature ajoute uniquement :

1. Une extension du modèle de sortie API existant (backend, non persisté).
2. Des jetons de design (frontend, non persistés — CSS uniquement).

## 1. Extension de l'API — `ChargeEntrainementOut`

Champ additionnel sur la réponse existante de `GET /api/dashboard/charge` (voir Decision 4 de `research.md`).

### PointChargeHistorique (nouveau)

| Champ | Type | Description |
|---|---|---|
| `date` | date (ISO 8601) | Fin de la semaine calendaire du point |
| `charge_aigue_7j` | float \| null | Charge aiguë calculée à cette date de référence |
| `charge_chronique_28j` | float \| null | Charge chronique calculée à cette date de référence |

### ChargeEntrainementOut (existant, étendu)

| Champ | Type | Statut |
|---|---|---|
| `charge_aigue_7j` | float \| null | inchangé |
| `charge_chronique_28j` | float \| null | inchangé |
| `ratio_acwr` | float \| null | inchangé |
| `tendance` | string \| null | inchangé |
| `donnees_suffisantes` | bool | inchangé |
| `historique` | `PointChargeHistorique[]` | **nouveau** — 8 points hebdomadaires les plus récents ; liste vide si `donnees_suffisantes=false` |

Aucun changement de comportement sur les champs existants (FR-008).

## 2. Jetons de design (frontend, CSS uniquement — non persistés)

Repris tels quels de la palette de référence validée du skill data-viz interne (voir Decision 2 de `research.md`). Déclarés comme variables CSS globales, consommés par tous les composants.

| Rôle | Usage dans l'application |
|---|---|
| Palette de statut (`good`/`warning`/`serious`/`critical`) | États de charge (normal/attention/surcharge) ; statuts de séance (valide/aberrant/doublon probable) |
| Rampe séquentielle bleue | Courbe de tendance de charge |
| Surface / encre primaire / secondaire / muted / gridline | Fond de page, typographie, grilles de graphique — cohérents sur les 5 pages (US3) |

Ces jetons ne sont pas des entités métier : ils n'ont pas de cycle de vie, ne sont ni créés ni supprimés par l'utilisateur, et vivent uniquement dans le code frontend (feuille de style).
