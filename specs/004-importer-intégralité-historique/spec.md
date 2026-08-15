# Feature Specification: Import complet de l'historique Strava et conservation illimitée

**Feature Branch**: `004-importer-intégralité-historique`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "fais en sorte que mon compte strava soit connecté, et récupère l'historique de mes séances. je veux toute les data" — précisé : import complet de l'historique (pas seulement 30 jours) ET conservation illimitée (pas de purge automatique à 3 mois).

**Relation à la spec 001** : cette feature modifie deux exigences de `specs/001-coaching-velo-garmin-strava/spec.md` :

- **FR-002** (import "nouvelles et historiques récentes") → remplacée par le FR-001 ci-dessous pour Strava : import de l'intégralité de l'historique disponible, pas seulement une fenêtre récente.
- **FR-012** (rétention glissante de 3 mois avec purge automatique) → **supprimée** par le FR-004 ci-dessous : conservation illimitée.

Le reste de la spec 001 (charge d'entraînement, recommandations, export/suppression RGPD, sécurité des tokens) reste inchangé.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Importer l'intégralité de mon historique Strava (Priority: P1)

En tant que cycliste, je connecte mon compte Strava et je veux que toutes mes séances historiques soient importées — pas seulement celles des 30 derniers jours — afin de disposer d'un historique complet pour l'analyse de charge et le suivi long terme.

**Why this priority**: C'est la demande explicite de l'utilisateur et le socle de valeur de cette feature — sans import complet, la conservation illimitée (US2) n'a rien à conserver au-delà de ce que l'import initial actuel fournit déjà.

**Independent Test**: Connecter un compte Strava réel possédant plus de 100 activités et/ou des activités de plus de 30 jours, et vérifier que `GET /api/seances` renvoie l'intégralité de ces activités après la synchronisation initiale — pas seulement les 100 ou 30 derniers jours les plus récents.

**Acceptance Scenarios**:

1. **Given** un compte Strava avec un historique de plusieurs années et plus de 100 activités, **When** l'athlète connecte ce compte pour la première fois, **Then** la totalité des activités disponibles sur Strava est importée, au-delà de la limite de pagination par défaut de l'API (100 par page) et au-delà de la fenêtre de 30 jours utilisée jusqu'ici.
2. **Given** un import en cours sur un historique volumineux, **When** l'API Strava applique une limite de débit temporaire (rate limit), **Then** l'import reprend automatiquement plutôt que d'échouer silencieusement ou de s'arrêter avec un sous-ensemble partiel non signalé.
3. **Given** une connexion Strava déjà active avant cette feature (avec seulement les 30 derniers jours importés), **When** l'athlète déclenche une resynchronisation, **Then** le reste de l'historique antérieur est également importé.

---

### User Story 2 - Conserver mes séances indéfiniment (Priority: P2)

En tant que cycliste, je veux que mes séances importées ne soient plus jamais supprimées automatiquement par le système, afin de conserver un historique complet pour analyser mes progrès sur plusieurs années.

**Why this priority**: Dépend de US1 pour avoir une réelle valeur (inutile de retirer la purge si l'import reste limité à 30 jours), mais reste vérifiable indépendamment sur les données déjà présentes.

**Independent Test**: Vérifier qu'aucun job planifié ne supprime de séances en fonction de leur ancienneté, en inspectant la configuration des jobs planifiés et en confirmant qu'une séance artificiellement vieille de plus de 3 mois n'est pas supprimée après l'heure à laquelle la purge se déclenchait auparavant.

**Acceptance Scenarios**:

1. **Given** des séances importées il y a plus de 3 mois, **When** le temps passe (ou le job planifié quotidien s'exécute), **Then** ces séances restent présentes dans `GET /api/seances`.
2. **Given** la fonctionnalité d'export et de suppression RGPD existante (spec 001, FR-013), **When** l'athlète exporte ou supprime explicitement ses données, **Then** ce droit reste pleinement fonctionnel — la conservation illimitée ne concerne que la purge *automatique*, pas le contrôle de l'athlète sur ses propres données.

---

### Edge Cases

- Que se passe-t-il si le compte Strava connecté a des milliers d'activités et que l'import volumineux prend plusieurs minutes voire heures du fait des limites de débit de l'API (100 requêtes/15 min, 1000/jour) ? L'athlète doit pouvoir constater une progression plutôt qu'une absence de réponse.
- Les séances déjà supprimées par la purge automatique avant cette feature sont définitivement perdues côté application — seule une resynchronisation complète depuis Strava peut les réimporter, et seulement si elles existent encore côté Strava.
- Que se passe-t-il si l'athlète déconnecte puis reconnecte Strava après cette feature ? Un nouvel import complet doit se redéclencher plutôt que de repartir seulement de la dernière synchronisation connue.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Lors de la première connexion Strava (ou d'une reconnexion), le système DOIT importer l'intégralité des activités disponibles sur le compte, sans limite de fenêtre temporelle (remplace FR-002 de la spec 001 pour la plateforme Strava).
- **FR-002**: Le système DOIT paginer les appels à l'API Strava afin de récupérer la totalité des activités, au-delà de la limite de 100 résultats par page.
- **FR-003**: Le système DOIT gérer les limites de débit de l'API Strava pendant un import volumineux en reprenant l'import après un délai plutôt qu'en échouant de façon silencieuse ou partielle.
- **FR-004**: Le système NE DOIT PLUS supprimer automatiquement de séances en fonction de leur ancienneté (supprime FR-012 et le job de purge de la spec 001) — la conservation devient illimitée par défaut.
- **FR-005**: Le système DOIT continuer de permettre à l'athlète d'exporter ou de supprimer explicitement l'ensemble de ses données à tout moment (FR-013 de la spec 001, inchangée) — la conservation illimitée automatique n'affecte pas ce droit.
- **FR-006**: Le système DOIT continuer d'appliquer la détection de doublons et le marquage des données aberrantes (FR-010/spec 001) sur l'historique complet importé, pas seulement sur les séances récentes.

### Key Entities

Aucune nouvelle entité — cette feature modifie le comportement d'import (`Séance`, `Connexion plateforme` de la spec 001) et retire un job planifié (purge), sans changement de modèle de données.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un athlète connectant un compte Strava avec un historique de plusieurs années voit 100% des activités Strava disponibles apparaître dans son historique applicatif après la synchronisation initiale (vérifiable en comparant le nombre d'activités Strava vs `GET /api/seances`).
- **SC-002**: Zéro séance n'est supprimée automatiquement par le système, quelle que soit son ancienneté, sur une période d'observation d'au moins 3 mois suivant le déploiement.
- **SC-003**: Un import de plus de 100 activités se termine avec succès (toutes les activités présentes) même en présence d'une limite de débit Strava temporaire pendant l'import.

## Assumptions

- Périmètre limité à Strava, à la demande explicite de l'utilisateur — les connecteurs Garmin Connect et Nolio ne sont pas modifiés par cette feature (ils ne sont pas connectés en pratique aujourd'hui).
- La suppression du job de purge automatique s'applique à toutes les séances (toutes plateformes confondues), puisque ce job n'était pas spécifique à Strava dans la spec 001 — effet secondaire accepté, sans impact pratique actuel.
- Les séances déjà supprimées par la purge automatique avant cette feature ne sont pas récupérables rétroactivement par l'application elle-même ; seule une resynchronisation complète depuis Strava peut les réimporter, si elles existent encore côté Strava.
- La conservation illimitée est un choix explicite de l'utilisateur pour cet usage personnel (mono-athlète, cf. spec 001) ; elle ne modifie pas le périmètre géographique RGPD (France/UE) ni le droit à l'export/suppression déjà garanti par FR-013.
- Aucune limite de volume de stockage n'est fixée par cette feature — la croissance de la base est acceptée comme conséquence directe de la conservation illimitée demandée.
