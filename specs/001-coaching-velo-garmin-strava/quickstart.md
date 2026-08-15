# Quickstart : Coaching vélo connecté

**Feature**: `001-coaching-velo-garmin-strava` | **Date**: 2026-08-15

Scénarios d'intégration pour valider chaque user story indépendamment, dans l'ordre de priorité (US1 → US2 → US3), conformément au Principe III (MVP incrémental).

## Prérequis

- Backend : Python 3.12, PostgreSQL 15+ démarré, variables d'environnement pour les secrets OAuth (`GARMIN_CLIENT_ID`/`SECRET`, `STRAVA_CLIENT_ID`/`SECRET`, `NOLIO_CLIENT_ID`/`SECRET`) — jamais committées (Contraintes & Confidentialité de la constitution).
- Frontend : Node.js 20.
- Un compte de test sur au moins une plateforme (Strava recommandé pour démarrer — flux OAuth 2.0 standard le plus simple à obtenir en sandbox).

```bash
# Backend
cd backend
uv venv && source .venv/bin/activate   # ou pip
uv sync                                 # installe FastAPI, SQLAlchemy, etc.
alembic upgrade head
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Scénario US1 — Importer automatiquement mes séances (P1)

**Correspond à**: spec.md Acceptance Scenarios 1-3 de US1, SC-001, SC-002.

1. Ouvrir l'application, aller sur la page Connexions.
2. Cliquer "Connecter Strava" → `POST /api/connexions/strava/autoriser` → redirection OAuth Strava (sandbox).
3. Autoriser l'accès → callback → `POST /api/connexions/strava/callback` finalise la connexion.
4. **Vérifier** : la connexion apparaît avec `statut = actif`, et les séances des 30 derniers jours du compte de test apparaissent dans `GET /api/seances` en moins de 5 minutes (SC-001).
5. Enregistrer une nouvelle activité sur le compte Strava de test.
6. **Vérifier** : après le prochain cycle de synchronisation planifiée (≤ 15 min), la séance apparaît via `GET /api/seances` (borne large de SC-002 : 95% sous 24h).
7. Révoquer manuellement l'accès côté Strava (dans les paramètres du compte de test).
8. **Vérifier** : au prochain cycle de sync, `ConnexionPlateforme.statut` passe à `expire`/`revoque` et l'UI affiche une invitation à reconnecter (FR-009).

*Ce scénario est testable sans que US2/US3 soient implémentées — aucun tableau de bord ni recommandation requis.*

## Scénario US2 — Comprendre ma charge d'entraînement (P2)

**Correspond à**: spec.md Acceptance Scenarios 1-3 de US2, SC-003.

Prérequis : au moins 2 semaines de séances importées (via US1, ou fixtures de test chargées directement en base pour un test isolé).

1. Ouvrir le Dashboard → `GET /api/dashboard/charge`.
2. **Vérifier** : la réponse contient `charge_aigue_7j`, `charge_chronique_28j`, `ratio_acwr`, `tendance`, et `donnees_suffisantes = true`.
3. Charger un jeu de séances simulant une forte hausse de charge sur les 7 derniers jours.
4. **Vérifier** : `tendance = surcharge` et l'UI affiche un signal visuel distinct (FR-005).
5. Repartir d'un compte sans historique (ou < 2 semaines).
6. **Vérifier** : `donnees_suffisantes = false`, l'UI affiche un message d'insuffisance de données plutôt qu'un graphique de tendance (évite l'analyse trompeuse, Acceptance Scenario 3).

*Testable avec des séances chargées directement (fixtures), indépendamment de US1 (mécanisme d'import) et de US3 (recommandations).*

## Scénario US3 — Recevoir des conseils de récupération et nutrition (P3)

**Correspond à**: spec.md Acceptance Scenarios 1-3 de US3, SC-005.

1. Renseigner le profil athlète (`PUT /api/athlete/profil` : poids, objectifs) — sans cela, voir étape 5.
2. Simuler l'import d'une séance à forte charge (via US1 ou fixture directe).
3. **Vérifier** : dans les 2 minutes, `GET /api/recommandations?type=recuperation` retourne une entrée `statut = disponible` avec un `contenu.repos_recommande` cohérent avec l'intensité (SC-005).
4. **Vérifier** : `GET /api/recommandations?type=nutrition` retourne une estimation calorique et macro cohérente avec le profil et la charge du jour.
5. Répéter avec un profil athlète vide (poids non renseigné).
6. **Vérifier** : la recommandation nutrition retourne `statut = donnees_insuffisantes` avec un `motif_donnees_insuffisantes` explicite — jamais une estimation par défaut (FR-011, Principe I NON-NEGOTIABLE, Acceptance Scenario 3).

*Testable en simulant une séance et un profil directement en base, indépendamment du reste du dashboard (US2).*

## Scénario transverse — Export et suppression RGPD (FR-013)

1. `GET /api/athlete/export` → vérifier que l'archive JSON contient profil, séances, connexions (sans tokens en clair), et recommandations.
2. `DELETE /api/athlete` → vérifier suppression en cascade en base et révocation des tokens OAuth actifs côté plateformes connectées.
