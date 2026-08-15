# Feature Specification: Refonte visuelle de l'application

**Feature Branch**: `002-améliore-design-application`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "Améliore grandement le design de l'application. je veux des graphiques, de la couleur, ect..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualiser sa charge d'entraînement d'un coup d'œil (Priority: P1)

En tant que cycliste, j'ouvre le tableau de bord et je vois immédiatement, grâce à un graphique clair et des couleurs signifiantes, l'évolution de ma charge d'entraînement dans le temps et mon état actuel (normal, surcharge, récupération), sans avoir à lire des chiffres bruts.

**Why this priority**: C'est la page d'atterrissage de l'application et la fonctionnalité la plus consultée (SC-003 de la spec 001 : identifier son état de charge en moins de 10 secondes). Le graphique actuel ne compare que deux points (charge chronique vs aiguë) et ne montre aucune tendance réelle dans le temps — c'est le manque le plus visible.

**Independent Test**: Peut être testé isolément en chargeant un historique de séances sur plusieurs semaines et en vérifiant que le tableau de bord affiche une courbe de tendance temporelle (pas seulement deux points), avec un code couleur cohérent pour l'état de charge (ex: vert = normal, orange = attention, rouge = surcharge).

**Acceptance Scenarios**:

1. **Given** un historique de séances sur au moins 4 semaines, **When** l'athlète ouvre le tableau de bord, **Then** un graphique affiche l'évolution de la charge chronique et aiguë jour par jour ou semaine par semaine (et non plus seulement deux points isolés).
2. **Given** un état de charge donné (normal, surcharge, récupération), **When** le tableau de bord est affiché, **Then** l'indicateur de charge et le graphique utilisent une couleur distincte et cohérente pour chaque état.
3. **Given** peu ou pas de données récentes, **When** le tableau de bord est affiché, **Then** le message "données insuffisantes" est présenté avec le même soin visuel que le reste de la page (pas un texte brut isolé).

---

### User Story 2 - Explorer visuellement l'historique de mes séances (Priority: P2)

En tant que cycliste, je consulte mon historique de séances et je peux repérer rapidement mes séances les plus intenses ou les plus longues grâce à une mise en forme visuelle (couleurs, mini-graphiques), plutôt qu'un tableau de texte brut.

**Why this priority**: L'historique est la deuxième page la plus consultée (après le tableau de bord) et contient déjà toute la donnée nécessaire (durée, distance, puissance, FC, dénivelé) ; aujourd'hui elle est rendue en table HTML sans hiérarchie visuelle ni code couleur, ce qui la rend difficile à parcourir rapidement.

**Independent Test**: Peut être testé isolément en chargeant une liste de séances variées (courtes/longues, intenses/légères) et en vérifiant que les séances se distinguent visuellement les unes des autres (couleur ou intensité liée à l'effort), et qu'une séance signalée (donnée aberrante, doublon probable) reste immédiatement reconnaissable.

**Acceptance Scenarios**:

1. **Given** une liste de séances avec des niveaux d'effort variés, **When** l'athlète consulte l'historique, **Then** chaque séance porte une indication visuelle (couleur ou icône) reflétant son intensité relative.
2. **Given** une séance marquée comme donnée aberrante ou doublon probable, **When** l'athlète consulte l'historique, **Then** cette séance reste clairement identifiable au premier coup d'œil (pas seulement via une petite mention textuelle).
3. **Given** une longue liste de séances, **When** l'athlète fait défiler la page, **Then** la lecture reste confortable (espacement, alternance visuelle des lignes, pas de mur de texte).

---

### User Story 3 - Bénéficier d'une identité visuelle cohérente sur toute l'application (Priority: P3)

En tant que cycliste, je navigue entre le tableau de bord, l'historique, les recommandations, les connexions et mon profil, et je retrouve partout la même palette de couleurs, la même typographie et les mêmes composants d'interface, ce qui rend l'application agréable et professionnelle à utiliser.

**Why this priority**: Une fois les deux pages les plus utilisées (tableau de bord, historique) visuellement enrichies, l'harmonisation du reste de l'application (recommandations, connexions, profil, navigation) complète l'expérience sans laquelle les deux premières pages resteraient des îlots visuellement incohérents avec le reste.

**Independent Test**: Peut être testé isolément en parcourant chacune des 5 pages de l'application et en vérifiant qu'elles partagent la même palette de couleurs, la même typographie, les mêmes styles de bouton/carte/badge, et que la navigation reflète clairement la page active.

**Acceptance Scenarios**:

1. **Given** l'athlète navigue d'une page à l'autre, **When** il compare deux pages quelconques, **Then** les couleurs, la typographie et les composants (cartes, badges, boutons) sont visuellement cohérents.
2. **Given** une recommandation de récupération ou nutritionnelle, **When** elle est affichée, **Then** elle est présentée avec une mise en forme visuelle distincte (carte, icône, couleur) plutôt qu'en texte brut, cohérente avec le reste de l'application.
3. **Given** l'athlète est sur une page donnée, **When** il regarde la navigation, **Then** la page active est visuellement mise en évidence.

---

### Edge Cases

- Que se passe-t-il si l'utilisateur a une préférence système pour le mode sombre ? (voir hypothèse ci-dessous sur le périmètre thème clair/sombre)
- Comment les couleurs d'état (charge normale/surcharge/récupération) restent-elles distinguables pour un utilisateur daltonien ?
- Que se passe-t-il visuellement quand une page est consultée sur un écran étroit (tablette) ? (le responsive mobile natif reste hors périmètre v1 selon la spec 001, mais l'app ne doit pas casser sur une largeur réduite de bureau/tablette)
- Comment le graphique de charge se comporte-t-il avec un historique très court (moins d'une semaine) ou au contraire très long (plusieurs mois) ?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT afficher sur le tableau de bord un graphique de l'évolution de la charge d'entraînement dans le temps (série temporelle), et non plus une comparaison à deux points isolés.
- **FR-002**: Le système DOIT utiliser un code couleur cohérent et constant à travers toute l'application pour représenter les états de charge (normal, surcharge, récupération) et les statuts d'anomalie de séance (valide, aberrant, doublon probable).
- **FR-003**: Le système DOIT présenter l'historique des séances avec une mise en forme visuelle (couleur ou indicateur graphique) reflétant l'intensité relative de chaque séance, en complément des données chiffrées déjà affichées.
- **FR-004**: Le système DOIT présenter les recommandations de récupération et de nutrition sous forme de cartes visuelles distinctes plutôt qu'en texte brut.
- **FR-005**: Le système DOIT appliquer une palette de couleurs, une typographie et des composants d'interface (cartes, badges, boutons) cohérents sur l'ensemble des pages (tableau de bord, historique, recommandations, connexions, profil).
- **FR-006**: Le système DOIT mettre en évidence visuellement la page actuellement active dans la navigation.
- **FR-007**: Le système DOIT conserver la lisibilité et le contraste des couleurs d'état pour rester perceptible par les utilisateurs daltonien(ne)s (ne pas s'appuyer sur la couleur seule pour distinguer un état critique).
- **FR-008**: Le système NE DOIT PAS dégrader les fonctionnalités existantes (import, calcul de charge, génération de recommandations, connexions, profil) : cette refonte est strictement visuelle, sans changement de comportement fonctionnel.

### Key Entities *(include if feature involves data)*

Cette fonctionnalité ne modifie aucune donnée métier ; elle change uniquement la présentation des entités déjà définies dans la spec 001 (Séance, Charge d'entraînement, Recommandation, Connexion plateforme, Athlète).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un athlète peut identifier son état de charge d'entraînement (normal, surcharge, récupération) en moins de 5 secondes de consultation du tableau de bord (amélioration du SC-003 de la spec 001, qui était de 10 secondes).
- **SC-002**: Le graphique de charge du tableau de bord affiche au moins 4 semaines d'évolution dans le temps, contre 2 points de comparaison actuellement.
- **SC-003**: Les 5 pages de l'application (tableau de bord, historique, recommandations, connexions, profil) partagent visuellement la même palette de couleurs et les mêmes composants d'interface, vérifiable par une revue visuelle croisée des pages.
- **SC-004**: Aucune régression fonctionnelle n'est introduite : les mêmes scénarios de validation que `quickstart.md` (spec 001) passent sans changement de comportement après la refonte.

## Assumptions

- Le style visuel (thème clair uniquement, ou clair + sombre) n'est pas précisé par l'utilisateur ; par défaut cette fonctionnalité livre un thème clair unique, cohérent et coloré. Le mode sombre pourra être une itération future si souhaité.
- Aucune nouvelle donnée métier n'est nécessaire : les graphiques et couleurs s'appuient sur les données déjà exposées par l'API existante (charge chronique/aiguë par période, métriques de séance, statuts).
- Le responsive mobile natif reste hors périmètre (cohérent avec l'hypothèse "web desktop" de la spec 001) ; seule la robustesse sur des largeurs de bureau/tablette réduites est attendue.
- L'identité visuelle (couleurs précises, ambiance graphique) est laissée à l'appréciation de l'implémentation lors de `/speckit.plan`, dans la limite d'une palette accessible (contraste suffisant, distinction daltonisme) et cohérente sur toute l'application.
