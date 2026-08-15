# CyclingMetrik

Application web de coaching pour cyclisme de compétition : import des séances (Garmin Connect / Strava / Nolio), analyse de la charge d'entraînement, et conseils personnalisés de récupération et de nutrition.

Construite avec la méthode [Spec-Driven Development](https://github.com/github/spec-kit) (Spec Kit) — voir `specs/001-coaching-velo-garmin-strava/` pour la spécification, le plan technique et les tâches.

## Stack

- **Backend** : Python 3.12, FastAPI, SQLAlchemy 2.0 + Alembic, PostgreSQL, APScheduler (jobs planifiés), httpx (connecteurs OAuth Garmin/Strava/Nolio)
- **Frontend** : React 18 + TypeScript, Vite, React Query, Recharts

## Lancer le backend

```bash
cd backend
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

cp .env.example .env
# Renseigner TOKEN_ENCRYPTION_KEY (python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
# et DATABASE_URL, puis les identifiants OAuth Strava/Garmin/Nolio si disponibles.

alembic upgrade head
uvicorn src.main:app --reload
```

L'API est servie sur `http://localhost:8000` (documentation interactive sur `/docs`).

### Tests backend

```bash
cd backend
source .venv/bin/activate
# Nécessite une base PostgreSQL de test accessible via DATABASE_URL (voir tests/conftest.py)
pytest
ruff check src tests
```

## Lancer le frontend

```bash
cd frontend
npm install
npm run dev
```

L'application est servie sur `http://localhost:5173` (proxy `/api` vers le backend sur le port 8000).

```bash
npm run lint   # eslint
npm run build  # type-check + build de production
```

## Structure du projet

```text
backend/
  src/
    models/          # Athlete, Séance, ChargeEntrainement, Recommandation, ConnexionPlateforme
    integrations/     # connecteurs Garmin Connect / Strava / Nolio (interface commune)
    services/
      training_load/    # calcul de charge (ACWR), tendance
      recommendations/  # règles de récupération + nutrition, garde-fou "données insuffisantes"
    api/               # routes FastAPI
    jobs/              # sync périodique, recalcul de charge, génération de recommandations, purge de rétention
  tests/
    contract/          # fixtures rejouables par plateforme source
    integration/        # scénarios par user story
    unit/               # calcul de charge, moteur de recommandations

frontend/
  src/
    pages/       # Dashboard, HistoriqueSeances, Recommandations, Connexions, Profil
    components/  # ChargeIndicator, ...
    services/    # client API
```

## Documentation Spec Kit

- `specs/001-coaching-velo-garmin-strava/spec.md` — spécification (user stories, exigences, critères de succès)
- `specs/001-coaching-velo-garmin-strava/plan.md` — plan technique et Constitution Check
- `specs/001-coaching-velo-garmin-strava/research.md` — décisions techniques (research.md)
- `specs/001-coaching-velo-garmin-strava/data-model.md` — modèle de données
- `specs/001-coaching-velo-garmin-strava/contracts/` — contrat API (OpenAPI) et interface des connecteurs
- `specs/001-coaching-velo-garmin-strava/quickstart.md` — scénarios d'intégration par user story
- `specs/001-coaching-velo-garmin-strava/tasks.md` — découpage en tâches (`/speckit.implement`)

## Workflow Spec Kit

```
/speckit.constitution   → principes du projet
/speckit.specify        → décrire une feature
/speckit.plan           → choix techniques (stack, architecture)
/speckit.tasks          → découpage en tâches actionnables
/speckit.implement      → exécution des tâches
```

Voir `CLAUDE.md` pour le workflow git (branches par feature, cadence de commit/push).
