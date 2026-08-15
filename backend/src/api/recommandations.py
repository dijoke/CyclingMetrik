from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.schemas import RecommandationOut
from src.db import get_db
from src.models.recommandation import Recommandation, TypeRecommandation
from src.services.athlete import obtenir_ou_creer_athlete

router = APIRouter(prefix="/api/recommandations", tags=["recommandations"])


@router.get("", response_model=list[RecommandationOut])
def lister_recommandations(
    type: TypeRecommandation | None = Query(default=None),
    db: Session = Depends(get_db),
):
    athlete = obtenir_ou_creer_athlete(db)
    requete = db.query(Recommandation).filter(Recommandation.athlete_id == athlete.id)
    if type is not None:
        requete = requete.filter(Recommandation.type == type)
    return requete.order_by(Recommandation.date_generation.desc()).all()
