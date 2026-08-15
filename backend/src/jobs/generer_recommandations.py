from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from src.db import SessionLocal
from src.models.recommandation import Recommandation
from src.models.seance import Seance, StatutDonneesSeance
from src.services.athlete import obtenir_ou_creer_athlete
from src.services.recommendations.moteur import generer_recommandations

INTERVALLE_MINUTES = 2  # SC-005 : recommandation disponible ≤ 2 min après import


def generer_pour_nouvelles_seances() -> None:
    db = SessionLocal()
    try:
        deja_couvertes = select(Recommandation.seance_declenchante_id).where(
            Recommandation.seance_declenchante_id.is_not(None)
        )
        seances_sans_recommandation = (
            db.query(Seance)
            .filter(Seance.statut_donnees == StatutDonneesSeance.VALIDE)
            .filter(~Seance.id.in_(deja_couvertes))
            .all()
        )
        if not seances_sans_recommandation:
            return

        athlete = obtenir_ou_creer_athlete(db)
        for seance in seances_sans_recommandation:
            generer_recommandations(db, athlete, seance_declenchante_id=seance.id)
    finally:
        db.close()


def enregistrer_job(scheduler: BackgroundScheduler) -> None:
    scheduler.add_job(
        generer_pour_nouvelles_seances,
        "interval",
        minutes=INTERVALLE_MINUTES,
        id="generer_recommandations",
        replace_existing=True,
    )
