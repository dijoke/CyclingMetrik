# Quickstart : Historique des séances enrichi

**Feature**: `007-historique-des-séances` | **Date**: 2026-08-15

## Prérequis

Backend + frontend démarrés, base migrée (nouvelle migration Alembic — 6 colonnes sur `seance`). Compte Strava déjà connecté (feature 004) avec un historique de séances, dont certaines avec capteur de puissance.

## Scénario US1 — Filtrer et trier (P1)

1. Ouvrir l'historique des séances.
2. Cliquer sur l'en-tête "Distance".
3. **Vérifier** : la liste se trie par distance ; un second clic inverse l'ordre.
4. Appliquer un filtre de plage de dates et/ou de statut.
5. **Vérifier** : seules les séances correspondantes restent affichées, avec un moyen de réinitialiser.

## Scénario US2 — Détail d'une séance (P2)

1. Cliquer sur une ligne de l'historique.
2. **Vérifier** : `GET /api/seances/{id}` est appelé et la page affiche les métriques complètes de cette séance.
3. Modifier l'URL avec un identifiant de séance inexistant.
4. **Vérifier** : une erreur claire s'affiche (404), pas une page vide.

## Scénario US3 — Records de puissance (P3)

1. Attendre que le job de backfill ait traité au moins quelques séances avec capteur de puissance (`flux_puissance_traite_le` renseigné en base).
2. Ouvrir le détail d'une séance traitée avec capteur de puissance.
3. **Vérifier** : les 5 valeurs de record (1/3/5/10/20 min) sont affichées, cohérentes avec la durée de la séance (pas de valeur pour une durée supérieure à la séance elle-même).
4. Ouvrir le détail d'une séance sans capteur de puissance.
5. **Vérifier** : l'absence de record est indiquée explicitement.
6. Vérifier en base que le backfill progresse sur l'historique complet au fil du temps (nombre de séances avec `flux_puissance_traite_le IS NOT NULL` qui augmente).

## Vérification de non-régression

Rejouer les quickstart.md des features 001, 002, 004 et 005 pour confirmer qu'aucun comportement existant n'a changé (FR-009).
