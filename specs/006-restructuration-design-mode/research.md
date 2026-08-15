# Research: Restructuration du design (mode sombre, navigation, vue d'ensemble)

**Feature**: `006-restructuration-design-mode` | **Date**: 2026-08-15

## Decision 1 — Mode sombre : valeurs de la palette de référence, activation via `prefers-color-scheme` + `data-theme`

**Rationale** : Le skill data-viz interne documente déjà des valeurs "dark" complètes pour chaque rôle de jeton déjà utilisé par `tokens.css` (surface, encre, gridline, statut) — reprises telles quelles plutôt qu'inventées :

| Rôle | Clair (déjà en place) | Sombre (nouveau) |
|---|---|---|
| `--surface-1` | `#fcfcfb` | `#1a1a19` |
| `--page-plane` | `#f9f9f7` | `#0d0d0d` |
| `--text-primary` | `#0b0b0b` | `#ffffff` |
| `--text-secondary` | `#52514e` | `#c3c2b7` |
| `--text-muted` | `#898781` | `#898781` (identique) |
| `--gridline` | `#e1e0d9` | `#2c2c2a` |
| `--border` | `rgba(11,11,11,0.10)` | `rgba(255,255,255,0.10)` |
| `--success-text` | `#006300` | `#0ca30c` |
| `--status-good/warning/serious/critical` | inchangés | identiques (palette de statut fixe, jamais thémée) |

Activation : valeurs claires sur `:root` (défaut), valeurs sombres sous `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {...} }` (suit le système) ET sous `:root[data-theme="dark"] {...}` (le choix explicite de l'utilisateur l'emporte dans les deux sens) — c'est exactement le patron documenté par le skill (FR-002/FR-003).

**Alternatives considered** :
- Inverser algorithmiquement les couleurs claires (filtre CSS `invert()`) — rejeté : casse les couleurs de statut et les graphiques, pas de garantie de contraste.
- Bibliothèque de thématisation tierce (ex. next-themes équivalent React) — rejetée : quelques lignes de React state + `localStorage` suffisent (Principe V), pas de nouvelle dépendance.

## Decision 2 — Couleurs de graphiques (Recharts) : paires clair/dark explicites par constante, pas une rampe séquentielle sombre complète

**Rationale** : `TrendChart`/`VolumeBarChart` utilisent des hex littéraux (attributs SVG `stroke`/`fill`, qui ne résolvent pas `var(...)`). Le skill ne publie pas de rampe séquentielle 100→700 pour surface sombre (uniquement la rampe claire et les 8 teintes catégorielles clair/dark). Plutôt que dériver et valider une nouvelle rampe complète, chaque couleur de graphique déjà utilisée se voit assigner une paire clair/dark tirée de valeurs **déjà publiées et validées** par le skill :

| Usage | Clair (déjà en place) | Sombre (nouveau) | Source |
|---|---|---|---|
| `TrendChart` — charge chronique | `#6da7ec` (séquentiel 300) | `#86b6ef` (séquentiel 250) | rampe séquentielle publiée |
| `TrendChart` — charge aiguë | `#184f95` (séquentiel 600) | `#3987e5` (catégoriel slot 1, dark) | teinte catégorielle publiée |
| `VolumeBarChart` — barres | `#256abf` (séquentiel 500) | `#3987e5` (catégoriel slot 1, dark) | teinte catégorielle publiée |
| Gridline/muted (graphiques) | `#e1e0d9` / `#898781` | `#2c2c2a` / `#898781` | chrome & ink publié |

**Alternatives considered** :
- Dériver et valider (script du skill) une rampe séquentielle sombre complète à 7 paliers — écarté : sur-ingénierie pour 3 constantes de couleur réellement utilisées (Principe V) ; les valeurs choisies restent 100% issues de la palette déjà validée, seulement recombinées.

## Decision 3 — Persistance du thème : `localStorage`, appliqué via `data-theme` sur `<html>`

**Rationale** : Un simple hook React lit `localStorage.getItem("theme")` au montage (ou l'absence → suit le système), applique `document.documentElement.dataset.theme` en conséquence, et écrit dans `localStorage` au clic sur le contrôle de bascule. Aucune dépendance, cohérent avec Decision 1.

**Alternatives considered** : Cookie + rendu serveur du thème — non applicable, l'application est une SPA sans rendu serveur.

## Decision 4 — Navigation : barre horizontale en haut, sans nouvelle dépendance de routage

**Rationale** : `react-router-dom` (déjà en place) ne change pas — seule la structure JSX/CSS de `App.tsx` passe d'une colonne latérale fixe à un `<header>` horizontal avec les mêmes `NavLink`. Aucun changement de route.

**Alternatives considered** : Sidebar rétractable plutôt que top-bar — écarté, l'utilisateur a explicitement demandé une barre horizontale façon application SaaS moderne.

## Decision 5 — Vue d'ensemble du tableau de bord : zéro nouvel endpoint, composition de données déjà exposées

**Rationale** : Les tuiles KPI (US3) réutilisent exclusivement `GET /api/dashboard/charge` (déjà consommé par `Dashboard.tsx`), `GET /api/statistiques/comparaison-annuelle` et `GET /api/statistiques/records` (specs 004/005, déjà exposés). Aucune agrégation ni endpoint nouveau nécessaire — confirme FR-008 (zéro changement fonctionnel).

**Alternatives considered** : Nouvel endpoint composite `/api/dashboard/apercu` regroupant les trois — écarté : les trois requêtes sont déjà rapides indépendamment (specs 004/005), un endpoint composite dupliquerait de la logique sans bénéfice mesurable pour 3 tuiles (Principe V).

## Résumé des NEEDS CLARIFICATION

Aucun.
