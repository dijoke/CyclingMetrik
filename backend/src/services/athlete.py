from __future__ import annotations

from sqlalchemy.orm import Session

from src.models.athlete import Athlete

_ATHLETE_EMAIL_DEFAUT = "athlete@localhost"


def obtenir_ou_creer_athlete(db: Session) -> Athlete:
    """V1 est mono-athlète par compte (Assumptions du spec) : un seul profil, créé à la volée."""
    athlete = db.query(Athlete).first()
    if athlete is None:
        athlete = Athlete(email=_ATHLETE_EMAIL_DEFAUT)
        db.add(athlete)
        db.commit()
        db.refresh(athlete)
    return athlete
