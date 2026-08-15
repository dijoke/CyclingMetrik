from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def demarrer() -> None:
    if not scheduler.running:
        scheduler.start()


def arreter() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
