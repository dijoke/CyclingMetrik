# Phase 0 Research: Coaching vélo connecté

**Feature**: `001-coaching-velo-garmin-strava` | **Date**: 2026-08-15

Ce document consolide les décisions techniques nécessaires pour lever les inconnues de la section Technical Context du plan, avant la conception détaillée (Phase 1).

## 1. Stack applicative

**Decision**: Backend Python 3.12 / FastAPI + PostgreSQL 15+ ; Frontend React 18 + TypeScript / Vite.

**Rationale**: Choix confirmé avec l'utilisateur. FastAPI + Pydantic donnent une validation stricte des données de séance (utile vu la variabilité des formats Garmin/Strava/Nolio) et un typage explicite des schémas de recommandation, ce qui sert directement le Principe I (recommandations explicables et fondées sur des données validées). PostgreSQL gère bien les séries temporelles de séances et les colonnes JSON pour les métadonnées de recommandation. React/TypeScript permet un tableau de bord interactif (graphiques de charge, tendances) requis par US2.

**Alternatives considered**: Node.js/NestJS pour un stack 100% TypeScript — écarté par préférence utilisateur, l'écosystème data Python (pandas/numpy) étant par ailleurs plus direct pour les calculs de charge d'entraînement. Rendu serveur simple (Jinja2) pour le frontend — écarté, jugé insuffisant pour l'interactivité attendue du dashboard (US2, SC-003).

## 2. Authentification aux plateformes sources (Garmin Connect, Strava, Nolio)

**Decision**: Un connecteur par plateforme (`backend/src/integrations/{garmin,strava,nolio}/`) implémentant une interface commune (`connect`, `refresh_token`, `fetch_activities_since`, `disconnect`), chacun utilisant le flux OAuth propre à sa plateforme :
- **Strava**: OAuth 2.0 standard (authorization code + refresh token), scope `activity:read_all`.
- **Garmin Connect**: OAuth via Garmin Connect Developer Program (PKCE), tokens à rafraîchir selon la politique du programme.
- **Nolio**: flux d'autorisation propre à la plateforme (à confirmer avec la documentation Nolio au moment de l'implémentation du connecteur — traité comme un détail d'implémentation encapsulé derrière l'interface commune, pas une inconnue bloquante pour le plan).

Tous les tokens (access + refresh) sont chiffrés at-rest (Fernet/`cryptography`) dans la table `connexion_plateforme`, jamais en clair, conformément au Principe II et à FR-001.

**Rationale**: Interface commune → US1 reste testable indépendamment par plateforme et une plateforme supplémentaire peut être ajoutée sans toucher au reste du système (Principe V, simplicité). Le detail exact du flux Nolio ne bloque pas le plan car il est isolé dans son propre connecteur.

**Alternatives considered**: Un connecteur générique paramétrable — écarté, chaque plateforme a des spécificités (pagination, format de charge/puissance) qui rendraient l'abstraction plus complexe que 3 implémentations simples de la même interface.

## 3. Synchronisation des séances (nouvelles + historique)

**Decision**: Import initial à la connexion (30 derniers jours, SC-001) via appel direct à l'API de la plateforme, puis synchronisation périodique planifiée (APScheduler, toutes les 15 minutes) qui interroge chaque connexion active pour les séances depuis `derniere_synchronisation`. Strava expose des webhooks — utilisables en complément pour réduire la latence, mais le polling périodique reste la garantie de repli commune aux 3 plateformes pour respecter SC-002 (95% sous 24h) sans dépendre de la fiabilité des webhooks de chaque plateforme.

**Rationale**: Le polling uniforme simplifie l'implémentation (Principe V) et couvre les 3 plateformes de façon identique. La marge de 24h (SC-002) est large par rapport à un intervalle de 15 minutes.

**Alternatives considered**: Webhooks uniquement — écarté car Garmin/Nolio n'offrent pas nécessairement la même fiabilité de push que Strava, et une dépendance exclusive au webhook romprait SC-002 en cas de notification manquée.

## 4. Planification des jobs (sync, purge de rétention)

**Decision**: APScheduler in-process (job périodique dans le processus backend), pas de file de messages séparée.

**Rationale**: Échelle v1 = mono-athlète par compte, volumétrie faible. Une infrastructure Celery + broker (Redis/RabbitMQ) ajouterait un service supplémentaire sans bénéfice mesurable à cette échelle (Principe V — complexité doit être justifiée).

**Alternatives considered**: Celery + Redis — écarté pour le MVP, à reconsidérer explicitement si le produit passe en multi-athlètes/coach (hors périmètre v1, cf. Assumptions du spec).

## 5. Modèle de calcul de la charge d'entraînement (US2)

**Decision**: Modèle de charge par séance basé sur la durée pondérée par l'intensité (TSS-like si puissance disponible, sinon hrTSS basé sur la fréquence cardiaque et la durée), agrégé en charge aiguë (7 jours) vs charge chronique (28 jours) pour dériver une tendance (progression / surcharge / récupération), inspiré du modèle ACWR (Acute:Chronic Workload Ratio) largement utilisé en science du sport.

**Rationale**: Modèle standard, explicable (Principe I — l'athlète peut voir les séances qui ont contribué au ratio), calculable sans dépendance externe. Fonctionne en dégradé sur fréquence cardiaque seule si pas de capteur de puissance (cf. Assumptions du spec).

**Alternatives considered**: Modèle propriétaire "boîte noire" (ex. score composite non documenté) — écarté, contraire au Principe I (recommandation/indicateur doit rester explicable).

## 6. Moteur de recommandations (récupération + nutrition, US3)

**Decision**: Moteur à règles explicites (pas de ML) : un ensemble de règles déterministes mappant (charge de la séance, ratio aigu/chronique récent, profil athlète) → recommandation de récupération et estimation nutritionnelle (formules établies : besoin calorique de base + surcoût d'activité, répartition glucides/protéines/lipides selon intensité). Chaque recommandation générée est stockée avec les identifiants des séances/données qui l'ont motivée (`justification`). Si les données requises sont absentes (profil incomplet, séance aberrante, historique insuffisant), le moteur retourne explicitement un statut "insuffisant" plutôt qu'une valeur par défaut (FR-011, Principe I NON-NEGOTIABLE).

**Rationale**: L'explicabilité et le garde-fou "pas de recommandation non fondée" sont une exigence non-négociable de la constitution ; un système à règles rend ce garde-fou trivial à vérifier et à tester (Principe IV, test-first).

**Alternatives considered**: Modèle ML entraîné sur des données d'athlètes — écarté pour la v1, non explicable par construction et sur-dimensionné pour le besoin (Principe V).

## 7. Détection de séances dupliquées entre plateformes (FR-010)

**Decision**: Règle de correspondance sur (date/heure de début à ±5 minutes, durée à ±2%, plateforme différente) → marquage "doublon probable", affiché à l'athlète plutôt que fusionné/supprimé automatiquement.

**Rationale**: Évite une fusion automatique risquée (perte de données) tout en signalant clairement le doublon (edge case du spec). L'athlète garde le contrôle, cohérent avec Principe I (pas de décision silencieuse sur des données ambiguës).

**Alternatives considered**: Fusion automatique silencieuse — écartée, risque de perte de la métrique la plus fiable entre les deux sources sans intervention de l'athlète.

## 8. Export et suppression des données (RGPD, FR-013)

**Decision**: Endpoint `GET /api/athlete/export` (export JSON de toutes les données de l'athlète : profil, séances, connexions, recommandations) et `DELETE /api/athlete` (suppression complète en cascade + révocation des tokens OAuth actifs). Traité comme fonctionnalité de première classe dans `contracts/`, pas une réflexion après-coup.

**Rationale**: Exigence explicite du Principe II et de FR-013 (RGPD France/UE).

**Alternatives considered**: Processus manuel (ticket support) — écarté, non conforme à l'exigence "à tout moment" du Principe II.

## Résumé des inconnues résolues

Toutes les inconnues de la section Technical Context du plan sont résolues ci-dessus. Aucun `NEEDS CLARIFICATION` restant.
