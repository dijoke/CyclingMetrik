# Research: Refonte visuelle de l'application

**Feature**: `002-améliore-design-application` | **Date**: 2026-08-15

État constaté du code avant décision (frontend) : `App.tsx` et les 5 pages (`Dashboard`, `HistoriqueSeances`, `Recommandations`, `Connexions`, `Profil`) sont entièrement en style inline, sans feuille de style ni dépendance de design. `Dashboard.tsx` utilise déjà `recharts` mais ne trace que 2 points isolés (charge chronique vs aiguë), pas une série temporelle. `HistoriqueSeances.tsx` est une table HTML brute. Aucun composant de carte/badge/bouton partagé n'existe.

## Decision 1 — Système de design : CSS natif (custom properties) plutôt qu'un framework

**Rationale**: L'application compte 5 pages et ~400 lignes de JSX au total, déjà 100% en style inline sans aucune dépendance CSS. Le besoin réel (palette cohérente + une poignée de composants réutilisables : carte, badge, bouton) ne justifie pas une nouvelle dépendance de build. Une feuille de style unique avec des variables CSS (`:root { --color-... }`) et quelques classes de composants suffit, reste sous contrôle total et respecte le Principe V (Simplicité & Dette Justifiée — toute nouvelle dépendance doit être justifiée).

**Alternatives considered**:
- Tailwind CSS — rejeté : nouvelle dépendance de build + changement d'outillage (PostCSS) disproportionné pour 5 pages.
- MUI / Chakra UI — rejeté : impose son propre système de composants et sa propre esthétique, bien plus lourd que le besoin, romprait avec l'approche "React simple" actuelle.
- styled-components / Emotion — rejeté : dépendance CSS-in-JS supplémentaire sans bénéfice net face à CSS natif + variables pour ce périmètre.

## Decision 2 — Palette de couleurs : réutiliser la palette de référence interne (data-viz), pas de palette ad hoc

**Rationale**: Le skill data-viz interne fournit une palette de référence déjà validée (séparation daltonisme CVD ΔE ≥ 8 sur les paires adjacentes, contrastes vérifiés, ordre catégoriel fixe) — l'utiliser directement satisfait FR-007 (distinction daltonisme) sans travail de validation supplémentaire. Le mapping est direct pour ce produit :
- palette de statut (`good` / `warning` / `serious` / `critical`) → états de charge (normal / attention / surcharge) et statuts de séance (valide / aberrant / doublon probable) ;
- rampe séquentielle bleue (100→700) → intensité/tendance de la courbe de charge ;
- jetons de surface/encre (primaire, secondaire, muted, gridline) → typographie et fond cohérents sur les 5 pages (US3).

**Alternatives considered**:
- Palette "vélo" custom (bleu/orange sport) — rejetée : demanderait sa propre validation d'accessibilité, travail dupliqué (Principe V).
- Conserver les couleurs actuelles ad hoc (`#0b5fff` bleu unique, `#b42318` rouge ponctuel) — rejetée : ne couvre ni les 3 états de charge ni les 2 statuts d'anomalie de façon cohérente, ce qui est précisément le manque à combler.

## Decision 3 — Graphiques : conserver Recharts, étendre son usage

**Rationale**: Recharts est déjà une dépendance du frontend (utilisée dans `Dashboard.tsx`, déjà actée au plan de la feature 001). Il couvre à la fois une courbe temporelle (US1) et un graphique de volume/intensité par séance (US2, ex. barres hebdomadaires). Aucune nouvelle dépendance nécessaire.

**Alternatives considered**:
- D3 direct — rejeté : trop bas niveau pour le besoin, Recharts suffit.
- Chart.js / visx — rejeté : nouvelle dépendance sans gain net face à Recharts déjà en place.

## Decision 4 — Série temporelle de charge : extension backend, pas de recalcul côté frontend

**Rationale**: `calculer_charge` (backend) encapsule la logique de charge (ACWR, seuils de surcharge/récupération), déjà couverte par des tests (Principe IV — test-first sur la logique d'analyse). FR-001 exige une vraie tendance temporelle (plusieurs points dans le temps), alors que `GET /api/dashboard/charge` n'expose aujourd'hui qu'un instantané (2 valeurs : chronique 28j, aiguë 7j). Recalculer une tendance simplifiée côté React à partir de `GET /api/seances` dupliquerait cette logique d'analyse sans tests (violation directe du Principe IV) et risquerait de diverger du calcul serveur.

**Approche retenue** : paramétrer `calculer_charge` avec une date de référence optionnelle, puis exposer un nouveau champ `historique` (liste de points hebdomadaires sur les 8 dernières semaines) sur l'endpoint existant `GET /api/dashboard/charge` — un seul appel réseau, calcul et tests côté backend avant toute implémentation frontend.

**Alternatives considered**:
- Dupliquer un calcul de tendance simplifié en frontend — rejeté : viole le Principe IV, risque de divergence.
- Nouvel endpoint séparé `GET /api/dashboard/charge/historique` — écarté au profit d'un champ additionnel sur l'endpoint existant : le tableau de bord a besoin des deux informations (instantané + historique) en même temps, autant les servir en un seul appel.

## Decision 5 — Mode sombre : hors périmètre

**Rationale**: déjà tranché comme hypothèse dans `spec.md` (thème clair par défaut, mode sombre = itération future possible). La palette de référence documente déjà des valeurs "dark" pour cette itération future si elle est priorisée, donc aucun travail n'est perdu.

## Résumé des NEEDS CLARIFICATION

Aucun — la spec ne portait aucun marqueur `[NEEDS CLARIFICATION]` et les 5 décisions ci-dessus couvrent l'intégralité du Technical Context.
