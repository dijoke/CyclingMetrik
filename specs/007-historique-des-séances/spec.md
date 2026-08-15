# Feature Specification: Historique des séances enrichi (filtres, détail, records de puissance)

**Feature Branch**: `007-historique-des-séances`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description : "dans la page historique : rajoute une manière de filtrer/trier les colonnes. Rajoute une colonne avec le record en watt séance sur 1min / 3min / 5min / 10min / 20min. Fais en sorte que je puisse cliquer sur la séance, pour pouvoir voir plein de détails sur la séance sur une autre page" — précisé : le backfill des records de puissance doit couvrir l'intégralité des séances déjà importées (787 séances), pas seulement les futures.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filtrer et trier l'historique de mes séances (Priority: P1)

En tant que cycliste avec des centaines de séances importées, je filtre et trie la liste par les colonnes affichées (date, durée, distance, puissance, statut...) afin de retrouver rapidement une séance précise sans faire défiler des centaines de lignes.

**Why this priority**: C'est la demande la plus simple et la plus autonome des trois — elle apporte une valeur immédiate sur les données déjà affichées aujourd'hui, sans dépendre d'aucune nouvelle donnée.

**Independent Test**: Charger une liste de séances variées et vérifier qu'un tri par une colonne (ex. distance décroissante) et un filtre (ex. période, statut) produisent le sous-ensemble et l'ordre attendus.

**Acceptance Scenarios**:

1. **Given** l'historique des séances est affiché, **When** l'athlète clique sur l'en-tête d'une colonne triable, **Then** la liste se trie selon cette colonne (et un second clic inverse l'ordre).
2. **Given** l'historique des séances est affiché, **When** l'athlète applique un filtre (ex. plage de dates, statut de donnée), **Then** seules les séances correspondantes restent affichées, avec un moyen visible de réinitialiser le filtre.
3. **Given** un filtre et un tri actifs, **When** l'athlète change de page puis revient sur l'historique, **Then** le comportement reste prévisible (l'état filtré n'induit pas en erreur — pas d'obligation de persistance entre navigations, mais pas de données manquantes/corrompues non plus).

---

### User Story 2 - Consulter le détail complet d'une séance (Priority: P2)

En tant que cycliste, je clique sur une séance dans l'historique pour ouvrir une page dédiée affichant tous ses détails (métriques complètes, statut, plateforme source), afin d'analyser une sortie précise sans être limité aux colonnes du tableau.

**Why this priority**: Rend l'historique réellement exploitable au-delà d'un tableau — et sert de point d'ancrage naturel pour les records de puissance (US3), qui s'affichent logiquement sur cette même page de détail plutôt que noyés dans le tableau principal.

**Independent Test**: Cliquer sur une séance dans l'historique et vérifier que la page de détail affiche des informations cohérentes avec cette séance précise (comparées à `GET /api/seances`), et qu'un retour vers l'historique est possible.

**Acceptance Scenarios**:

1. **Given** l'historique des séances est affiché, **When** l'athlète clique sur une ligne de séance, **Then** il est amené vers une page dédiée à cette séance, affichant ses métriques complètes.
2. **Given** la page de détail d'une séance, **When** l'athlète consulte les informations, **Then** il retrouve au minimum : date, durée, distance, dénivelé, puissance moyenne, fréquence cardiaque moyenne, plateforme source, statut de données.
3. **Given** une séance inexistante ou n'appartenant pas à l'athlète, **When** la page de détail est demandée, **Then** l'application affiche une erreur claire plutôt qu'un contenu vide ou trompeur.

---

### User Story 3 - Voir mes records de puissance par durée (Priority: P3)

En tant que cycliste équipé d'un capteur de puissance, je vois, pour chaque séance concernée, mes meilleures puissances moyennes tenues sur 1, 3, 5, 10 et 20 minutes, afin d'évaluer mes points forts et ma progression à différentes intensités — une lecture que le seul chiffre de puissance moyenne sur la séance entière ne permet pas.

**Why this priority**: Dépend de l'existence d'une donnée qui n'est pas encore collectée (flux de puissance seconde par seconde) — c'est la story la plus coûteuse techniquement et la moins immédiate, mais celle qui apporte l'analyse la plus fine.

**Independent Test**: Sur une séance avec capteur de puissance et un historique de flux disponible, vérifier que les 5 valeurs de record affichées correspondent à la meilleure moyenne glissante réellement atteignable sur la séance pour chaque durée.

**Acceptance Scenarios**:

1. **Given** une séance avec un capteur de puissance et dont les données de flux ont été traitées, **When** l'athlète consulte le détail de cette séance, **Then** il voit ses 5 meilleures puissances moyennes (1/3/5/10/20 min).
2. **Given** une séance sans capteur de puissance (aucune puissance moyenne enregistrée), **When** l'athlète consulte son détail, **Then** l'absence de record de puissance est indiquée explicitement plutôt qu'une valeur à zéro trompeuse.
3. **Given** une séance plus courte qu'une des durées de référence (ex. 15 minutes de séance pour un record 20 min), **When** les records sont affichés, **Then** seule cette durée précise est indiquée comme non applicable, sans affecter les autres durées atteignables.
4. **Given** l'intégralité de l'historique déjà importé (787 séances) au moment de la mise en service de cette feature, **When** le traitement de fond s'exécute, **Then** les séances avec capteur de puissance voient progressivement leurs records calculés, sans action manuelle de l'athlète, et sans bloquer le reste de l'application pendant le traitement.

---

### Edge Cases

- Une séance dont le flux de puissance n'est plus disponible côté plateforme source (supprimée, activité rendue privée entre-temps) doit être marquée comme traitée-sans-résultat, pas retentée indéfiniment.
- Le traitement de fond du backfill (US3) doit respecter les limites de débit de l'API Strava déjà gérées par l'application (feature 004) — un grand nombre de séances à traiter ne doit pas dégrader la synchronisation normale des nouvelles séances.
- Un tri ou un filtre appliqué à une colonne dont certaines séances n'ont pas la donnée (ex. puissance absente) doit placer ces séances de façon prévisible (ex. en fin de liste) plutôt que de provoquer une erreur.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT permettre de trier l'historique des séances par au moins : date, durée, distance, dénivelé, puissance moyenne.
- **FR-002**: Le système DOIT permettre de filtrer l'historique des séances par au moins : plage de dates, statut de donnée (valide/aberrant/doublon probable).
- **FR-003**: Le système DOIT permettre à l'athlète d'accéder à une page de détail dédiée pour chaque séance en cliquant dessus depuis l'historique.
- **FR-004**: La page de détail DOIT afficher au minimum : date, durée, distance, dénivelé, puissance moyenne, fréquence cardiaque moyenne, plateforme source, statut de données.
- **FR-005**: Le système DOIT calculer, pour chaque séance disposant d'un capteur de puissance, la meilleure puissance moyenne glissante sur 1, 3, 5, 10 et 20 minutes.
- **FR-006**: Le système DOIT indiquer explicitement l'absence de record de puissance (pas de capteur, séance trop courte pour une durée donnée, ou flux non disponible) plutôt qu'une valeur par défaut trompeuse.
- **FR-007**: Le système DOIT traiter l'intégralité des séances déjà importées au moment du déploiement de cette feature (backfill), en tâche de fond, sans bloquer la synchronisation normale des nouvelles séances ni l'utilisation de l'application pendant le traitement.
- **FR-008**: Le système NE DOIT PAS retenter indéfiniment le calcul de records pour une séance dont le flux de puissance n'est pas disponible côté plateforme source.
- **FR-009**: Le système NE DOIT PAS modifier le comportement existant de l'historique (import, détection de doublons, statuts de données) — cette feature ajoute des capacités de consultation et une nouvelle donnée calculée, sans changer les données déjà exposées par les specs 001/002/004.

### Key Entities

- **Séance** (existante, spec 001) : étendue avec cinq valeurs optionnelles de record de puissance (1/3/5/10/20 min) et un marqueur d'état de traitement du flux, permettant de distinguer "pas encore traité" de "traité, aucune donnée disponible".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un athlète peut retrouver une séance précise parmi plusieurs centaines en moins de 15 secondes grâce au tri/filtre, contre un défilement manuel aujourd'hui.
- **SC-002**: 100% des séances disposant d'une puissance moyenne enregistrée voient leur traitement de records de puissance tenté (traité avec résultat, ou explicitement marqué sans donnée disponible) dans les jours suivant le déploiement, sans intervention manuelle.
- **SC-003**: La page de détail d'une séance est accessible en un clic depuis l'historique.

## Assumptions

- Les records de puissance sont calculés à partir du flux de puissance déjà fourni par Strava pour les activités avec capteur — aucune nouvelle donnée n'est demandée à l'athlète.
- Le traitement de fond respecte les limites de débit déjà gérées pour Strava (feature 004, research.md) ; un backfill complet de l'historique existant peut prendre plusieurs heures à quelques jours selon le volume, ce qui est accepté (confirmé par l'utilisateur).
- Garmin Connect et Nolio ne sont pas concernés par cette feature (non connectés en pratique aujourd'hui, cohérent avec le périmètre Strava déjà établi en feature 004).
- Le filtrage/tri reste côté client pour cette version (volume actuel : ~800 séances, largement gérable sans pagination serveur) ; non persistant entre les navigations, cohérent avec la simplicité attendue (Principe V).
