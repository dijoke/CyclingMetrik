from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.schemas import ChargeEntrainementOut
from src.db import get_db
from src.services.athlete import obtenir_ou_creer_athlete
from src.services.training_load.calcul_charge import calculer_charge

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/charge", response_model=ChargeEntrainementOut)
def charge_courante(db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    return calculer_charge(db, athlete.id)
