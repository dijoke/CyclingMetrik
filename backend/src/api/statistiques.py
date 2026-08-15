from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.schemas import (
    ComparaisonAnnuelleOut,
    RecordsPersonnelsOut,
    StatAnnuelleOut,
    StatMensuelleOut,
)
from src.db import get_db
from src.services.athlete import obtenir_ou_creer_athlete
from src.services.statistiques.agregats import (
    comparaison_annuelle,
    records_personnels,
    statistiques_annuelles,
    statistiques_mensuelles,
)

router = APIRouter(prefix="/api/statistiques", tags=["statistiques"])


@router.get("/annuelles", response_model=list[StatAnnuelleOut])
def annuelles(db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    return statistiques_annuelles(db, athlete.id)


@router.get("/annuelles/{annee}/mensuelles", response_model=list[StatMensuelleOut])
def mensuelles(annee: int, db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    return statistiques_mensuelles(db, athlete.id, annee)


@router.get("/records", response_model=RecordsPersonnelsOut)
def records(db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    return records_personnels(db, athlete.id)


@router.get("/comparaison-annuelle", response_model=ComparaisonAnnuelleOut)
def comparaison(db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    return comparaison_annuelle(db, athlete.id, datetime.now(UTC))
