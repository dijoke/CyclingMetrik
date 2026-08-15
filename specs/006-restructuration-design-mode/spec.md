# Feature Specification: Restructuration du design (mode sombre, navigation, vue d'ensemble)

**Feature Branch**: `006-restructuration-design-mode`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "Fais une restructuration du design du site. Je veux un design plus au goût du jour" — précisé : mode sombre + polish visuel, ET restructuration de la mise en page (navigation top-bar plutôt que sidebar, tableau de bord avec tuiles KPI en un coup d'œil).

**Relation aux specs précédentes** : cette feature s'appuie sur le système de design déjà en place (spec 002 : `tokens.css`, `Card`, `StatusBadge`, palette de référence) et les endpoints déjà disponibles (specs 001/004/005) — elle ne modifie aucune donnée ni aucun comportement fonctionnel, uniquement la présentation et la structure de navigation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Choisir un thème clair ou sombre (Priority: P1)

En tant qu'utilisateur, je choisis entre un thème clair et un thème sombre (ou je laisse l'application suivre la préférence de mon système), afin de consulter l'application confortablement quelle que soit la luminosité ambiante — un mode sombre étant aujourd'hui un standard attendu d'une application moderne.

**Why this priority**: C'est l'élément le plus concrètement associé à un design "au goût du jour" et le plus autonome à livrer — il ne dépend d'aucune restructuration de mise en page pour apporter de la valeur.

**Independent Test**: Basculer le thème via un contrôle visible dans l'interface et vérifier que l'ensemble des pages (pas seulement la page courante) passe au thème sombre, avec un contraste texte/fond suffisant partout, et que le choix est mémorisé après un rechargement de la page.

**Acceptance Scenarios**:

1. **Given** l'application est ouverte, **When** l'utilisateur n'a jamais choisi de thème, **Then** l'application suit la préférence sombre/claire de son système d'exploitation.
2. **Given** l'utilisateur bascule explicitement le thème via un contrôle dans l'interface, **When** il navigue vers une autre page ou recharge l'application, **Then** son choix explicite est conservé et prime sur la préférence système.
3. **Given** le thème sombre est actif, **When** l'utilisateur consulte n'importe quelle page (tableau de bord, historique, statistiques, recommandations, connexions, profil), **Then** tous les textes, graphiques et badges de statut restent lisibles avec un contraste suffisant.

---

### User Story 2 - Naviguer via une barre de navigation moderne (Priority: P2)

En tant qu'utilisateur, je navigue entre les pages via une barre de navigation horizontale en haut de l'écran plutôt qu'une barre latérale, pour une mise en page qui exploite mieux la largeur disponible et se rapproche des applications web actuelles.

**Why this priority**: Restructure la mise en page globale — dépend d'être fait après ou indépendamment du thème (US1), mais avant que la vue d'ensemble (US3) ait un cadre stable dans lequel s'intégrer.

**Independent Test**: Vérifier que la navigation horizontale permet d'atteindre les 6 pages existantes, que la page active est mise en évidence, et que le contenu principal occupe la largeur laissée disponible sans la colonne latérale fixe actuelle.

**Acceptance Scenarios**:

1. **Given** l'application est ouverte, **When** l'utilisateur regarde le haut de l'écran, **Then** il voit une barre de navigation horizontale listant les 6 pages (tableau de bord, historique, statistiques, recommandations, connexions, profil).
2. **Given** l'utilisateur est sur une page donnée, **When** il regarde la barre de navigation, **Then** la page active est visuellement mise en évidence (cohérent avec le comportement déjà existant en sidebar, spec 002 FR-006).
3. **Given** la barre de navigation remplace la sidebar, **When** l'utilisateur consulte n'importe quelle page, **Then** aucune fonctionnalité existante n'est perdue ou rendue inaccessible.

---

### User Story 3 - Voir un aperçu global dès l'ouverture du tableau de bord (Priority: P3)

En tant qu'utilisateur, j'ouvre le tableau de bord et je vois immédiatement un ensemble de tuiles résumant mon état global (charge actuelle, volume de l'année en cours vs l'an dernier, nombre de séances, un record marquant) avant même de dérouler le graphique de tendance détaillé, afin d'avoir une vue d'ensemble en un coup d'œil.

**Why this priority**: Complète la modernisation visuelle en tirant parti des données déjà exposées (specs 004/005) pour transformer le tableau de bord en un vrai point d'entrée synthétique — mais reste un ajout au tableau de bord existant, pas un prérequis pour US1/US2.

**Independent Test**: Charger un compte avec un historique de séances et vérifier que les tuiles affichées reflètent des données réellement cohérentes avec `GET /api/dashboard/charge`, `GET /api/statistiques/comparaison-annuelle` et `GET /api/statistiques/records` déjà disponibles.

**Acceptance Scenarios**:

1. **Given** un historique de séances suffisant, **When** l'utilisateur ouvre le tableau de bord, **Then** il voit en haut de la page des tuiles résumant : l'état de charge actuel, le volume cumulé de l'année en cours, et un record personnel marquant — avant le détail (courbe de tendance) déjà existant.
2. **Given** des données insuffisantes pour une tuile donnée (ex. pas de comparaison année précédente disponible), **When** le tableau de bord est affiché, **Then** cette tuile indique explicitement l'absence de donnée plutôt qu'une valeur trompeuse (cohérent avec spec 001 Principe I et spec 005 FR-006).

---

### Edge Cases

- Un système dont le thème ne peut pas être détecté (navigateur ne supportant pas `prefers-color-scheme`) doit afficher le thème clair par défaut, pas une page cassée.
- Une page consultée sur une largeur d'écran réduite (tablette) avec la nouvelle navigation top-bar ne doit pas casser l'affichage (cohérent avec l'hypothèse "web desktop" de la spec 001 — robustesse sur largeur réduite, pas responsive mobile natif complet).
- Les graphiques (Recharts) déjà présents doivent rester lisibles en thème sombre — leurs couleurs ne doivent pas se fondre dans un fond sombre.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT permettre à l'utilisateur de basculer explicitement entre thème clair et thème sombre via un contrôle visible dans l'interface.
- **FR-002**: Le système DOIT, en l'absence de choix explicite, suivre la préférence système (`prefers-color-scheme`) de l'utilisateur.
- **FR-003**: Le système DOIT mémoriser le choix explicite de l'utilisateur entre les sessions (rechargement de page).
- **FR-004**: Le système DOIT appliquer le thème choisi de façon cohérente sur les 6 pages existantes, y compris les graphiques et badges de statut, avec un contraste suffisant.
- **FR-005**: Le système DOIT remplacer la navigation latérale (sidebar) par une navigation horizontale (top-bar) donnant accès aux 6 pages existantes, avec mise en évidence de la page active (cohérent avec FR-006 de la spec 002).
- **FR-006**: Le système DOIT afficher, en haut du tableau de bord, un aperçu synthétique (tuiles) de l'état de charge actuel, du volume cumulé de l'année en cours, et d'au moins un record personnel — avant le détail existant (graphique de tendance).
- **FR-007**: Le système DOIT indiquer explicitement l'absence de donnée pour une tuile de l'aperçu plutôt que d'afficher une valeur par défaut trompeuse.
- **FR-008**: Le système NE DOIT PAS changer de comportement fonctionnel (données affichées, calculs, flux OAuth, etc.) — cette feature reste strictement une restructuration visuelle et de mise en page.

### Key Entities

Aucune nouvelle entité, aucun nouvel endpoint — cette feature réutilise exclusivement les données déjà exposées par les specs 001/002/004/005 (charge, statistiques, records) et ajoute un état de préférence d'affichage (thème) qui n'est pas une donnée métier.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un utilisateur peut basculer entre thème clair et sombre en un clic, sans rechargement de page.
- **SC-002**: Le choix de thème est conservé à 100% des rechargements de page suivants.
- **SC-003**: Un utilisateur peut identifier son état global (charge, volume annuel, un record) en moins de 5 secondes de consultation du tableau de bord, sans dérouler le détail.
- **SC-004**: Aucune régression fonctionnelle : les scénarios de validation des specs 001, 002, 004 et 005 passent sans changement de comportement après cette restructuration.

## Assumptions

- Le thème sombre réutilise les valeurs déjà documentées dans la palette de référence du skill data-viz interne (research.md de la spec 002 mentionnait déjà cette possibilité comme itération future) — pas de nouvelle palette inventée.
- La police reste la police système déjà utilisée (`system-ui` et équivalents) — pas de nouvelle police web chargée depuis un service externe, cohérent avec la préférence de simplicité déjà actée en spec 002.
- Aucun nouvel endpoint backend n'est nécessaire : l'aperçu du tableau de bord (US3) réutilise exclusivement des endpoints déjà existants (`GET /api/dashboard/charge`, `GET /api/statistiques/comparaison-annuelle`, `GET /api/statistiques/records`).
- Le responsive mobile natif complet reste hors périmètre (cohérent avec l'hypothèse "web desktop" de la spec 001) ; seule la robustesse sur largeur réduite est attendue pour la nouvelle navigation.
