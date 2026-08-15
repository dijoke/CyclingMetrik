from __future__ import annotations

import logging
from datetime import UTC, datetime

from apscheduler.schedulers.background import BackgroundScheduler

from src.db import SessionLocal
from src.integrations.base import PlateformeIndisponibleError, TokenInvalideError
from src.integrations.strava.connecteur import StravaConnecteur
from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme, StatutConnexion
from src.models.seance import Seance
from src.services.import_seances import tokens_depuis_connexion
from src.services.puissance.records import RecordsPuissanceSeance, calculer_records_puissance

logger = logging.getLogger("coaching_velo")

INTERVALLE_MINUTES = 2
TAILLE_LOT = 20  # research.md Decision 4 : borné pour ne pas concurrencer sync_seances sur le débit Strava


def _appliquer_records(seance: Seance, records: RecordsPuissanceSeance) -> None:
    seance.puissance_max_1min = records.puissance_max_1min
    seance.puissance_max_3min = records.puissance_max_3min
    seance.puissance_max_5min = records.puissance_max_5min
    seance.puissance_max_10min = records.puissance_max_10min
    seance.puissance_max_20min = records.puissance_max_20min
    seance.flux_puissance_traite_le = datetime.now(UTC)


def traiter_lot_records_puissance() -> None:
    """Backfill + traitement des nouvelles séances : calcule les records de puissance par durée
    pour un lot borné de séances Strava non encore traitées (FR-005/FR-007). Les séances sans
    puissance moyenne sont marquées traitées sans appel réseau (pas de capteur = pas de flux).
    """
    db = SessionLocal()
    try:
        seances = (
            db.query(Seance)
            .join(ConnexionPlateforme, Seance.connexion_plateforme_id == ConnexionPlateforme.id)
            .filter(
                Seance.flux_puissance_traite_le.is_(None),
                ConnexionPlateforme.plateforme == Plateforme.STRAVA,
            )
            .limit(TAILLE_LOT)
            .all()
        )
        if not seances:
            return

        connecteur = StravaConnecteur()
        connexions: dict = {}

        for seance in seances:
            if seance.puissance_moyenne_watts is None:
                seance.flux_puissance_traite_le = datetime.now(UTC)
                db.commit()
                continue

            connexion = connexions.get(seance.connexion_plateforme_id)
            if connexion is None:
                connexion = (
                    db.query(ConnexionPlateforme).filter_by(id=seance.connexion_plateforme_id).first()
                )
                connexions[seance.connexion_plateforme_id] = connexion

            if connexion is None or connexion.statut != StatutConnexion.ACTIF:
                continue

            try:
                flux = connecteur.recuperer_flux_puissance(tokens_depuis_connexion(connexion), seance.id_externe)
            except TokenInvalideError:
                logger.warning("Connexion %s expirée — traitement des records reporté", connexion.id)
                return
            except PlateformeIndisponibleError:
                logger.warning("Strava indisponible — traitement des records reporté au prochain cycle")
                return

            _appliquer_records(seance, calculer_records_puissance(flux))
            db.commit()
    finally:
        db.close()


def enregistrer_job(scheduler: BackgroundScheduler) -> None:
    scheduler.add_job(
        traiter_lot_records_puissance,
        "interval",
        minutes=INTERVALLE_MINUTES,
        id="calculer_records_puissance",
        replace_existing=True,
    )
