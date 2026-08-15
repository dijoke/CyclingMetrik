from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import athlete, connexions, dashboard, recommandations, seances, statistiques
from src.api.middleware import configurer_gestion_erreurs
from src.jobs import calculer_records_puissance, generer_recommandations, recompute_charge, sync_seances
from src.jobs import scheduler as job_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    sync_seances.enregistrer_job(job_scheduler.scheduler)
    recompute_charge.enregistrer_job(job_scheduler.scheduler)
    generer_recommandations.enregistrer_job(job_scheduler.scheduler)
    calculer_records_puissance.enregistrer_job(job_scheduler.scheduler)
    job_scheduler.demarrer()
    yield
    job_scheduler.arreter()


app = FastAPI(title="Coaching vélo connecté", lifespan=lifespan)
configurer_gestion_erreurs(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connexions.router)
app.include_router(seances.router)
app.include_router(dashboard.router)
app.include_router(recommandations.router)
app.include_router(athlete.router)
app.include_router(statistiques.router)
