from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.schemas import SeanceOut
from src.db import get_db
from src.models.seance import Seance, StatutDonneesSeance
from src.services.athlete import obtenir_ou_creer_athlete

router = APIRouter(prefix="/api/seances", tags=["seances"])


@router.get("", response_model=list[SeanceOut])
def lister_seances(
    depuis: date | None = Query(default=None),
    statut_donnees: StatutDonneesSeance | None = Query(default=None),
    db: Session = Depends(get_db),
):
    athlete = obtenir_ou_creer_athlete(db)
    requete = db.query(Seance).filter(Seance.athlete_id == athlete.id)
    if depuis is not None:
        requete = requete.filter(Seance.date_debut >= depuis)
    if statut_donnees is not None:
        requete = requete.filter(Seance.statut_donnees == statut_donnees)
    return requete.order_by(Seance.date_debut.desc()).all()
