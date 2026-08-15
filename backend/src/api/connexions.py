from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import AutorisationOut, CallbackInput, ConnexionPlateformeOut
from src.db import get_db
from src.integrations.base import TokenInvalideError
from src.integrations.garmin.connecteur import GarminConnecteur
from src.integrations.nolio.connecteur import NolioConnecteur
from src.integrations.strava.connecteur import StravaConnecteur
from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme, StatutConnexion
from src.security.token_crypto import chiffrer
from src.services.athlete import obtenir_ou_creer_athlete
from src.services.import_seances import importer_seances, tokens_depuis_connexion

router = APIRouter(prefix="/api/connexions", tags=["connexions"])

CONNECTEURS = {
    Plateforme.STRAVA: StravaConnecteur(),
    Plateforme.GARMIN_CONNECT: GarminConnecteur(),
    Plateforme.NOLIO: NolioConnecteur(),
}

REDIRECT_URI_BASE = "http://localhost:8000/api/connexions"


def _connexion_existante(db: Session, athlete_id, plateforme: Plateforme) -> ConnexionPlateforme | None:
    return db.query(ConnexionPlateforme).filter_by(athlete_id=athlete_id, plateforme=plateforme).first()


@router.get("", response_model=list[ConnexionPlateformeOut])
def lister_connexions(db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    return db.query(ConnexionPlateforme).filter(ConnexionPlateforme.athlete_id == athlete.id).all()


@router.post("/{plateforme}/autoriser", response_model=AutorisationOut)
def autoriser(plateforme: Plateforme):
    connecteur = CONNECTEURS[plateforme]
    state = secrets.token_urlsafe(16)
    redirect_uri = f"{REDIRECT_URI_BASE}/{plateforme.value}/callback"
    return AutorisationOut(url_autorisation=connecteur.url_autorisation(redirect_uri, state))


@router.post("/{plateforme}/callback", response_model=ConnexionPlateformeOut, status_code=201)
def callback(plateforme: Plateforme, payload: CallbackInput, db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    connecteur = CONNECTEURS[plateforme]
    redirect_uri = f"{REDIRECT_URI_BASE}/{plateforme.value}/callback"
    try:
        tokens = connecteur.echanger_code(payload.code, redirect_uri)
    except TokenInvalideError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    connexion = _connexion_existante(db, athlete.id, plateforme)
    if connexion is None:
        connexion = ConnexionPlateforme(athlete_id=athlete.id, plateforme=plateforme)
        db.add(connexion)

    connexion.statut = StatutConnexion.ACTIF
    connexion.access_token_chiffre = chiffrer(tokens.access_token)
    connexion.refresh_token_chiffre = (
        chiffrer(tokens.refresh_token) if tokens.refresh_token else None
    )
    connexion.date_expiration_token = tokens.expire_le
    db.commit()
    db.refresh(connexion)

    importer_seances(db, connexion, connecteur)
    db.refresh(connexion)
    return connexion


@router.delete("/{plateforme}", status_code=204)
def deconnecter(plateforme: Plateforme, db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    connexion = _connexion_existante(db, athlete.id, plateforme)
    if connexion is None:
        raise HTTPException(status_code=404, detail="Connexion introuvable")

    connecteur = CONNECTEURS[plateforme]
    connecteur.revoquer(tokens_depuis_connexion(connexion))
    connexion.statut = StatutConnexion.REVOQUE
    db.commit()
