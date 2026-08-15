from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.schemas import AthleteOut, AthleteProfilInput
from src.db import get_db
from src.models.connexion_plateforme import ConnexionPlateforme
from src.models.recommandation import Recommandation
from src.models.seance import Seance
from src.services.athlete import obtenir_ou_creer_athlete
from src.services.import_seances import tokens_depuis_connexion

router = APIRouter(prefix="/api/athlete", tags=["athlete"])


@router.get("/profil", response_model=AthleteOut)
def consulter_profil(db: Session = Depends(get_db)):
    return obtenir_ou_creer_athlete(db)


@router.put("/profil", response_model=AthleteOut)
def modifier_profil(payload: AthleteProfilInput, db: Session = Depends(get_db)):
    athlete = obtenir_ou_creer_athlete(db)
    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(athlete, champ, valeur)
    db.commit()
    db.refresh(athlete)
    return athlete


@router.get("/export")
def exporter_donnees(db: Session = Depends(get_db)):
    """Export complet des données de l'athlète — RGPD, FR-013, Principe II."""
    athlete = obtenir_ou_creer_athlete(db)
    connexions = db.query(ConnexionPlateforme).filter_by(athlete_id=athlete.id).all()
    seances = db.query(Seance).filter_by(athlete_id=athlete.id).all()
    recommandations = db.query(Recommandation).filter_by(athlete_id=athlete.id).all()

    return {
        "profil": AthleteOut.model_validate(athlete).model_dump(mode="json"),
        "connexions": [
            {
                "plateforme": c.plateforme.value,
                "statut": c.statut.value,
                "date_connexion": c.date_connexion.isoformat(),
                "date_derniere_synchronisation": (
                    c.date_derniere_synchronisation.isoformat()
                    if c.date_derniere_synchronisation
                    else None
                ),
            }
            for c in connexions
        ],
        "seances": [
            {
                "date_debut": s.date_debut.isoformat(),
                "duree_secondes": s.duree_secondes,
                "distance_metres": (
                    float(s.distance_metres) if s.distance_metres is not None else None
                ),
                "puissance_moyenne_watts": (
                    float(s.puissance_moyenne_watts)
                    if s.puissance_moyenne_watts is not None
                    else None
                ),
                "frequence_cardiaque_moyenne": s.frequence_cardiaque_moyenne,
                "denivele_metres": (
                    float(s.denivele_metres) if s.denivele_metres is not None else None
                ),
                "statut_donnees": s.statut_donnees.value,
            }
            for s in seances
        ],
        "recommandations": [
            {
                "type": r.type.value,
                "date_generation": r.date_generation.isoformat(),
                "statut": r.statut.value,
                "contenu": r.contenu,
                "justification": r.justification,
            }
            for r in recommandations
        ],
    }


@router.delete("", status_code=204)
def supprimer_compte(db: Session = Depends(get_db)):
    """Suppression complète en cascade + révocation des tokens actifs — RGPD, FR-013."""
    from src.api.connexions import CONNECTEURS

    athlete = obtenir_ou_creer_athlete(db)
    connexions = db.query(ConnexionPlateforme).filter_by(athlete_id=athlete.id).all()

    for connexion in connexions:
        try:
            CONNECTEURS[connexion.plateforme].revoquer(tokens_depuis_connexion(connexion))
        except Exception:
            pass  # la révocation distante ne doit pas bloquer la suppression du compte

    db.delete(athlete)  # cascade DB (ondelete="CASCADE") vers connexions/séances/recommandations
    db.commit()
