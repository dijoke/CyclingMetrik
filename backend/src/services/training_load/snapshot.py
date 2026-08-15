from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from src.models.charge_entrainement import ChargeEntrainement
from src.services.training_load.calcul_charge import calculer_charge


def enregistrer_snapshot(db: Session, athlete_id: uuid.UUID) -> ChargeEntrainement | None:
    """Persiste un instantané de charge pour l'historique de tendance ; None si insuffisant."""
    resultat = calculer_charge(db, athlete_id)
    if not resultat.donnees_suffisantes:
        return None

    snapshot = ChargeEntrainement(
        athlete_id=athlete_id,
        date_calcul=resultat.date_calcul,
        charge_aigue_7j=resultat.charge_aigue_7j,
        charge_chronique_28j=resultat.charge_chronique_28j,
        ratio_acwr=resultat.ratio_acwr,
        tendance=resultat.tendance,
        donnees_suffisantes=resultat.donnees_suffisantes,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot
