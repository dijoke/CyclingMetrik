from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from src.db import SessionLocal
from src.integrations.base import PlateformeIndisponibleError, TokenInvalideError
from src.models.connexion_plateforme import ConnexionPlateforme, StatutConnexion
from src.services.detection_doublons import detecter_doublons
from src.services.import_seances import importer_seances

logger = logging.getLogger("coaching_velo")

INTERVALLE_MINUTES = 15  # research.md §3 : large marge par rapport à SC-002 (95% sous 24h)


def synchroniser_toutes_connexions() -> None:
    from src.api.connexions import CONNECTEURS

    db = SessionLocal()
    try:
        connexions = db.query(ConnexionPlateforme).filter_by(statut=StatutConnexion.ACTIF).all()
        for connexion in connexions:
            connecteur = CONNECTEURS[connexion.plateforme]
            try:
                importer_seances(db, connexion, connecteur)
                detecter_doublons(db, connexion.athlete_id)
            except TokenInvalideError:
                connexion.statut = StatutConnexion.EXPIRE
                db.commit()
                logger.warning("Connexion %s expirée — athlète à notifier (FR-009)", connexion.id)
            except PlateformeIndisponibleError:
                logger.warning(
                    "Plateforme %s indisponible, synchronisation reportée au prochain cycle",
                    connexion.plateforme,
                )
    finally:
        db.close()


def enregistrer_job(scheduler: BackgroundScheduler) -> None:
    scheduler.add_job(
        synchroniser_toutes_connexions,
        "interval",
        minutes=INTERVALLE_MINUTES,
        id="sync_seances",
        replace_existing=True,
    )
