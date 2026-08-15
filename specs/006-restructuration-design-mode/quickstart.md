# Quickstart : Restructuration du design

**Feature**: `006-restructuration-design-mode` | **Date**: 2026-08-15

## Prérequis

Backend + frontend démarrés (aucun changement backend requis pour cette feature — research.md Decision 5). Un navigateur permettant de simuler `prefers-color-scheme` (DevTools) pour valider US1.

## Scénario US1 — Mode sombre (P1)

1. Ouvrir l'application avec la préférence système en mode sombre (DevTools → Rendering → `prefers-color-scheme: dark`), sans avoir jamais basculé le thème manuellement.
2. **Vérifier** : l'application s'affiche en thème sombre par défaut (FR-002).
3. Basculer explicitement vers le thème clair via le contrôle de l'interface.
4. **Vérifier** : l'application passe en clair, et reste en clair même si la préférence système repasse en sombre (FR-003, le choix explicite prime).
5. Recharger la page.
6. **Vérifier** : le thème clair choisi est conservé (FR-003, SC-002).
7. Parcourir les 6 pages en thème sombre.
8. **Vérifier** : textes, graphiques et badges de statut restent lisibles partout (FR-004).

## Scénario US2 — Navigation top-bar (P2)

1. Ouvrir l'application.
2. **Vérifier** : une barre de navigation horizontale en haut de l'écran liste les 6 pages (FR-005).
3. Naviguer vers chaque page.
4. **Vérifier** : la page active est mise en évidence, aucune fonctionnalité existante n'est inaccessible (Acceptance Scenario 3).

## Scénario US3 — Vue d'ensemble du tableau de bord (P3)

1. Ouvrir le tableau de bord avec un historique de séances couvrant au moins deux années.
2. **Vérifier** : des tuiles résumant l'état de charge, le volume de l'année en cours, et un record personnel s'affichent avant le détail existant (FR-006).
3. **Vérifier** manuellement la cohérence des tuiles avec `GET /api/dashboard/charge`, `GET /api/statistiques/comparaison-annuelle` et `GET /api/statistiques/records`.

## Vérification de non-régression

Rejouer `specs/001-coaching-velo-garmin-strava/quickstart.md`, `specs/002-améliore-design-application/quickstart.md`, `specs/004-importer-intégralité-historique/quickstart.md` et `specs/005-exploiter-les-années/quickstart.md` pour confirmer qu'aucun comportement fonctionnel n'a changé (FR-008, SC-004).
