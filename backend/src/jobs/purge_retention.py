from __future__ import annotations

from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from src.db import SessionLocal
from src.models.seance import Seance

RETENTION = timedelta(days=90)  # FR-012 : rétention glissante de 3 mois


def purger_seances_expirees() -> int:
    db = SessionLocal()
    try:
        seuil = datetime.now(UTC) - RETENTION
        nb_supprimees = (
            db.query(Seance).filter(Seance.date_debut < seuil).delete(synchronize_session=False)
        )
        db.commit()
        return nb_supprimees
    finally:
        db.close()


def enregistrer_job(scheduler: BackgroundScheduler) -> None:
    scheduler.add_job(
        purger_seances_expirees,
        "cron",
        hour=3,
        minute=0,
        id="purge_retention",
        replace_existing=True,
    )
