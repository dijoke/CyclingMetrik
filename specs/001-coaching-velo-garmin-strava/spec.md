# Feature Specification: Coaching vélo connecté (import séances + conseils récupération/nutrition)

**Feature Branch**: `001-coaching-velo-garmin-strava`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "Application web de coaching pour cyclisme de competition qui recupere les seances depuis Garmin Connect, Strava ou Nolio, analyse la charge d'entrainement et conseille l'athlete sur la recuperation, la nutrition et les apports necessaires"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Importer automatiquement mes séances (Priority: P1)

En tant que cycliste en compétition, je connecte mon compte Garmin Connect, Strava ou Nolio à l'application pour que mes séances (sorties, home-trainer, courses) soient importées automatiquement, sans ressaisie manuelle, avec leurs métriques (durée, distance, puissance, fréquence cardiaque, dénivelé).

**Why this priority**: Sans données de séances fiables et à jour, aucune analyse ni conseil n'est possible. C'est le socle de toute la valeur de l'application.

**Independent Test**: Peut être testé isolément en connectant un compte Garmin Connect ou Strava de test et en vérifiant que les dernières séances apparaissent dans l'application avec les bonnes métriques, sans aucune fonctionnalité d'analyse ou de conseil active.

**Acceptance Scenarios**:

1. **Given** un compte Garmin Connect ou Strava valide, **When** l'athlète autorise la connexion depuis l'application, **Then** ses séances des 30 derniers jours sont importées et affichées dans un historique.
2. **Given** une connexion déjà établie, **When** une nouvelle séance est enregistrée sur la plateforme source, **Then** elle apparaît dans l'application dans un délai raisonnable sans action manuelle de l'athlète.
3. **Given** une connexion à une plateforme source qui devient invalide (token expiré, accès révoqué), **When** l'application tente une synchronisation, **Then** l'athlète est averti clairement et invité à reconnecter son compte.

---

### User Story 2 - Comprendre ma charge d'entraînement et mon état de forme (Priority: P2)

En tant que cycliste, je consulte un tableau de bord qui traduit mes séances importées en indicateurs de charge d'entraînement (volume, intensité, tendance de charge dans le temps) afin de savoir si je suis en phase de progression, de surcharge ou de récupération.

**Why this priority**: Une fois les données disponibles (US1), l'analyse est ce qui transforme des chiffres bruts en information exploitable pour piloter l'entraînement.

**Independent Test**: Peut être testé en chargeant un jeu de séances historiques et en vérifiant que le tableau de bord affiche une charge d'entraînement cohérente et une tendance (hausse/baisse/stable), indépendamment des conseils de récupération/nutrition.

**Acceptance Scenarios**:

1. **Given** un historique d'au moins 2 semaines de séances importées, **When** l'athlète ouvre le tableau de bord, **Then** il voit sa charge d'entraînement récente et son évolution sur les 4 dernières semaines.
2. **Given** une charge d'entraînement en forte hausse sur une courte période, **When** le tableau de bord est affiché, **Then** un signal visuel indique un risque de surcharge.
3. **Given** peu ou pas de données récentes, **When** l'athlète ouvre le tableau de bord, **Then** l'application indique clairement que les données sont insuffisantes plutôt que d'afficher une analyse trompeuse.

---

### User Story 3 - Recevoir des conseils de récupération et nutrition (Priority: P3)

En tant que cycliste, je reçois après chaque séance importante (ou chaque jour) des recommandations personnalisées sur ma récupération (repos, sommeil, intensité du lendemain) et ma nutrition (besoins caloriques et apports glucidiques/protéiques estimés) en fonction de la charge de la séance et de mon état de forme.

**Why this priority**: C'est la valeur ajoutée finale du produit, mais elle dépend entièrement de la fiabilité des données (US1) et de l'analyse de charge (US2) pour être pertinente et ne pas induire l'athlète en erreur.

**Independent Test**: Peut être testé en simulant une séance à forte charge et en vérifiant qu'un conseil de récupération et une estimation nutritionnelle cohérents sont générés, indépendamment du reste du tableau de bord.

**Acceptance Scenarios**:

1. **Given** une séance intense vient d'être importée, **When** l'analyse est terminée, **Then** l'athlète reçoit une recommandation de récupération (ex: repos, sommeil, ou séance légère) adaptée à l'intensité de la séance.
2. **Given** le profil de l'athlète (poids, objectifs) et la charge du jour, **When** les conseils sont générés, **Then** une estimation des apports caloriques et de la répartition glucides/protéines/lipides du jour est affichée.
3. **Given** des données de séance insuffisantes ou incohérentes, **When** l'application tente de générer un conseil, **Then** elle évite de donner une recommandation nutritionnelle ou de récupération non fondée et indique le manque de données.

---

### Edge Cases

- Que se passe-t-il si l'athlète connecte plusieurs plateformes (Garmin Connect + Strava) qui contiennent la même séance en double ?
- Comment l'application gère-t-elle une séance importée avec des données aberrantes (ex: fréquence cardiaque de capteur défaillant) ?
- Que se passe-t-il si l'athlète n'a renseigné aucune donnée de profil (poids, objectifs) au moment où un conseil nutritionnel est demandé ?
- Comment l'application réagit-elle en cas d'indisponibilité temporaire de l'API d'une plateforme source (Garmin, Strava, Nolio) ?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT permettre à l'athlète de connecter au moins un compte parmi Garmin Connect, Strava ou Nolio via un flux d'autorisation sécurisé (sans stocker ses identifiants en clair).
- **FR-002**: Le système DOIT importer automatiquement les séances (nouvelles et historiques récentes) depuis les plateformes connectées, avec leurs métriques principales (durée, distance, puissance si disponible, fréquence cardiaque, dénivelé).
- **FR-003**: Le système DOIT permettre à l'athlète de visualiser un historique de ses séances importées, classées chronologiquement.
- **FR-004**: Le système DOIT calculer et afficher un indicateur de charge d'entraînement agrégé, ainsi que sa tendance récente.
- **FR-005**: Le système DOIT signaler à l'athlète une tendance de surcharge ou de sous-récupération lorsqu'elle est détectée.
- **FR-006**: Le système DOIT générer, après chaque séance significative, une recommandation de récupération adaptée à l'intensité et à la charge cumulée récente.
- **FR-007**: Le système DOIT générer une estimation des besoins nutritionnels journaliers (calories et macronutriments) en fonction du profil de l'athlète et de la charge d'entraînement.
- **FR-008**: Le système DOIT permettre à l'athlète de renseigner et modifier son profil (poids, taille, objectifs, contraintes alimentaires éventuelles) utilisé pour personnaliser les conseils.
- **FR-009**: Le système DOIT informer l'athlète lorsqu'une connexion à une plateforme source devient invalide et l'inviter à la reconnecter.
- **FR-010**: Le système DOIT détecter et signaler les séances potentiellement dupliquées lorsque plusieurs plateformes sources sont connectées simultanément.
- **FR-011**: Le système MUST NOT afficher de conseil de récupération ou de nutrition lorsque les données disponibles sont insuffisantes pour le fonder ; il DOIT alors indiquer explicitement ce manque de données.

- **FR-012**: Le système DOIT conserver l'historique des séances importées pendant 3 mois glissants, puis purger automatiquement les séances au-delà de cette période.
- **FR-013**: Le système DOIT permettre à l'athlète d'exporter ou de supprimer ses données personnelles conformément au RGPD (utilisateurs situés en France/UE ; aucune autre juridiction visée pour cette v1).

### Key Entities *(include if feature involves data)*

- **Athlète**: Profil de l'utilisateur — poids, taille, objectifs de compétition, contraintes alimentaires, comptes de plateformes connectés.
- **Séance**: Un entraînement ou une course importé(e) d'une plateforme source — date, durée, distance, puissance, fréquence cardiaque, dénivelé, plateforme d'origine.
- **Charge d'entraînement**: Indicateur agrégé calculé à partir des séances sur une période donnée, avec sa tendance (hausse, stable, baisse).
- **Recommandation**: Conseil généré (récupération ou nutrition) associé à une séance ou à une période, avec sa justification (données ayant motivé le conseil).
- **Connexion plateforme**: Association entre l'athlète et un compte externe (Garmin Connect, Strava, Nolio) — statut (actif, expiré, révoqué), date de dernière synchronisation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un athlète peut connecter un compte Garmin Connect ou Strava et voir ses séances des 30 derniers jours importées en moins de 5 minutes.
- **SC-002**: 95% des séances enregistrées sur une plateforme connectée apparaissent dans l'application dans les 24 heures suivant leur enregistrement.
- **SC-003**: Un athlète peut identifier son état de charge d'entraînement (normal, surcharge, récupération) en moins de 10 secondes de consultation du tableau de bord.
- **SC-004**: 90% des séances importées ne nécessitent aucune correction manuelle de la part de l'athlète pour être exploitables dans l'analyse.
- **SC-005**: Un conseil de récupération ou de nutrition est disponible dans les 2 minutes suivant l'import d'une séance significative.

## Assumptions

- L'athlète dispose d'un compte actif sur au moins une des plateformes supportées (Garmin Connect, Strava ou Nolio) et peut y donner un accès en lecture à l'application.
- Le public cible est un seul athlète compétiteur par compte (pas de gestion multi-athlètes/coach dans cette première version).
- Les recommandations de récupération et nutrition sont des estimations informatives destinées à accompagner l'entraînement, pas des prescriptions médicales ou diététiques individualisées ; l'athlète reste responsable de ses décisions de santé.
- La disponibilité des métriques de puissance dépend du capteur utilisé par l'athlète (capteur de puissance, home-trainer connecté) ; en son absence, l'analyse de charge s'appuie sur la fréquence cardiaque et la durée/distance.
- Le web est la plateforme cible pour cette première version (pas d'application mobile native dans le périmètre initial).
