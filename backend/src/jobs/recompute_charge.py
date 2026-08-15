from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from src.db import SessionLocal
from src.models.athlete import Athlete
from src.services.training_load.snapshot import enregistrer_snapshot

INTERVALLE_MINUTES = 15


def recalculer_charge_tous_athletes() -> None:
    db = SessionLocal()
    try:
        for athlete in db.query(Athlete).all():
            enregistrer_snapshot(db, athlete.id)
    finally:
        db.close()


def enregistrer_job(scheduler: BackgroundScheduler) -> None:
    scheduler.add_job(
        recalculer_charge_tous_athletes,
        "interval",
        minutes=INTERVALLE_MINUTES,
        id="recompute_charge",
        replace_existing=True,
    )
