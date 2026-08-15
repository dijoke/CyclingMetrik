from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.schemas import ChargeEntrainementOut, PointChargeHistoriqueOut
from src.db import get_db
from src.services.athlete import obtenir_ou_creer_athlete
from src.services.training_load.calcul_charge import calculer_charge, historique_charge

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/charge", response_model=ChargeEntrainementOut)
def charge_courante(db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    charge = calculer_charge(db, athlete.id)
    historique = historique_charge(db, athlete.id)
    return ChargeEntrainementOut(
        date_calcul=charge.date_calcul,
        charge_aigue_7j=charge.charge_aigue_7j,
        charge_chronique_28j=charge.charge_chronique_28j,
        ratio_acwr=charge.ratio_acwr,
        tendance=charge.tendance,
        donnees_suffisantes=charge.donnees_suffisantes,
        historique=[
            PointChargeHistoriqueOut(
                date=point.date,
                charge_aigue_7j=point.charge_aigue_7j,
                charge_chronique_28j=point.charge_chronique_28j,
            )
            for point in historique
        ],
    )
