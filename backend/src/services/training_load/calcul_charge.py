from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from src.models.seance import Seance, StatutDonneesSeance

FENETRE_AIGUE = timedelta(days=7)
FENETRE_CHRONIQUE = timedelta(days=28)
HISTORIQUE_MIN = timedelta(days=14)  # US2 Acceptance Scenario 3 : < 2 semaines → données insuffisantes

SEUIL_SURCHARGE = 1.5  # ACWR usuel en science du sport (research.md §5)
SEUIL_RECUPERATION = 0.8
INTENSITE_NEUTRE_DEFAUT = 100  # utilisée si ni puissance ni FC disponibles pour une séance


@dataclass
class ChargeResultat:
    date_calcul: datetime
    charge_aigue_7j: float | None
    charge_chronique_28j: float | None
    ratio_acwr: float | None
    tendance: str | None
    donnees_suffisantes: bool


def _charge_seance(seance: Seance) -> float:
    """Charge par séance : durée (heures) pondérée par l'intensité.

    Utilise la puissance si disponible (proxy TSS-like), sinon la fréquence cardiaque
    (proxy hrTSS), sinon une intensité neutre par défaut (research.md §5 ; dégradation
    prévue par les Assumptions du spec en l'absence de capteur de puissance).
    """
    duree_h = seance.duree_secondes / 3600
    if seance.puissance_moyenne_watts:
        return duree_h * float(seance.puissance_moyenne_watts)
    if seance.frequence_cardiaque_moyenne:
        return duree_h * seance.frequence_cardiaque_moyenne
    return duree_h * INTENSITE_NEUTRE_DEFAUT


def _tendance(ratio: float, charge_chronique_debut: float, charge_chronique_fin: float) -> str:
    if ratio > SEUIL_SURCHARGE:
        return "surcharge"
    if ratio < SEUIL_RECUPERATION:
        return "recuperation"
    if charge_chronique_fin > charge_chronique_debut * 1.05:
        return "progression"
    return "stable"


def calculer_charge(db: Session, athlete_id: uuid.UUID) -> ChargeResultat:
    maintenant = datetime.now(UTC)
    premiere_seance = (
        db.query(Seance)
        .filter(Seance.athlete_id == athlete_id, Seance.statut_donnees == StatutDonneesSeance.VALIDE)
        .order_by(Seance.date_debut)
        .first()
    )
    if premiere_seance is None or (maintenant - premiere_seance.date_debut) < HISTORIQUE_MIN:
        return ChargeResultat(
            date_calcul=maintenant,
            charge_aigue_7j=None,
            charge_chronique_28j=None,
            ratio_acwr=None,
            tendance=None,
            donnees_suffisantes=False,
        )

    seances_28j = (
        db.query(Seance)
        .filter(
            Seance.athlete_id == athlete_id,
            Seance.statut_donnees == StatutDonneesSeance.VALIDE,
            Seance.date_debut >= maintenant - FENETRE_CHRONIQUE,
        )
        .all()
    )
    seances_7j = [s for s in seances_28j if s.date_debut >= maintenant - FENETRE_AIGUE]
    seances_28j_debut = [
        s for s in seances_28j if s.date_debut < maintenant - FENETRE_CHRONIQUE + FENETRE_AIGUE
    ]

    charge_aigue = sum(_charge_seance(s) for s in seances_7j)
    charge_chronique = sum(_charge_seance(s) for s in seances_28j) / 4
    charge_chronique_debut = (
        sum(_charge_seance(s) for s in seances_28j_debut) if seances_28j_debut else charge_chronique
    )

    ratio = charge_aigue / charge_chronique if charge_chronique > 0 else 0.0

    return ChargeResultat(
        date_calcul=maintenant,
        charge_aigue_7j=round(charge_aigue, 1),
        charge_chronique_28j=round(charge_chronique, 1),
        ratio_acwr=round(ratio, 2),
        tendance=_tendance(ratio, charge_chronique_debut, charge_chronique),
        donnees_suffisantes=True,
    )
