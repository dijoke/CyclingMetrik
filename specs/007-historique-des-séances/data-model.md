# Data Model: Historique des séances enrichi (filtres, détail, records de puissance)

**Feature**: `007-historique-des-séances` | **Date**: 2026-08-15

## Extension de `Séance` (existante, spec 001)

Nouvelle migration Alembic ajoutant 6 colonnes nullable — aucune colonne existante modifiée, aucune donnée existante affectée (FR-009).

| Colonne | Type | Description |
|---|---|---|
| `puissance_max_1min` | float \| null | Meilleure puissance moyenne glissante sur 60s |
| `puissance_max_3min` | float \| null | Idem, 180s |
| `puissance_max_5min` | float \| null | Idem, 300s |
| `puissance_max_10min` | float \| null | Idem, 600s |
| `puissance_max_20min` | float \| null | Idem, 1200s |
| `flux_puissance_traite_le` | datetime \| null | Marqueur de traitement (research.md Decision 4) — distingue "pas encore traité" (`null`) de "traité, éventuellement sans résultat" (horodatage renseigné). Champ interne, non exposé par l'API. |

Chaque `puissance_max_*` est indépendamment `null` si la séance est plus courte que la durée correspondante, si aucun capteur de puissance n'était présent, ou si le flux n'a pas pu être récupéré (FR-006/FR-008) — jamais une valeur par défaut trompeuse.

## Objet de calcul (non persisté)

### RecordsPuissanceSeance

Résultat de la fonction pure de calcul (research.md Decision 3), avant écriture en base :

| Champ | Type |
|---|---|
| `puissance_max_1min` | float \| null |
| `puissance_max_3min` | float \| null |
| `puissance_max_5min` | float \| null |
| `puissance_max_10min` | float \| null |
| `puissance_max_20min` | float \| null |

## API — `SeanceOut` étendu

Le schéma existant `SeanceOut` (spec 001) gagne les 5 champs `puissance_max_*` (le marqueur `flux_puissance_traite_le` reste interne, non exposé). Utilisé à la fois par `GET /api/seances` (liste, déjà existant) et le nouveau `GET /api/seances/{id}` (detail, US2).
