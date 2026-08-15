from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from src.models.athlete import Athlete
from src.models.recommandation import Recommandation, StatutRecommandation, TypeRecommandation
from src.services.recommendations.nutrition import generer_estimation_nutrition
from src.services.recommendations.recuperation import generer_recommandation_recuperation
from src.services.training_load.calcul_charge import ChargeResultat, calculer_charge


def generer_recommandations(
    db: Session, athlete: Athlete, seance_declenchante_id: uuid.UUID | None = None
) -> list[Recommandation]:
    """Génère récupération + nutrition. Chaque recommandation impose l'invariant du Principe I
    (NON-NEGOTIABLE) par construction : jamais de `contenu` sans `justification`, jamais un
    statut `disponible` sans données pour le fonder — voir data-model.md §Recommandation.
    """
    charge = calculer_charge(db, athlete.id)

    recommandations = [
        _construire_recuperation(athlete, charge, seance_declenchante_id),
        _construire_nutrition(athlete, charge, seance_declenchante_id),
    ]
    db.add_all(recommandations)
    db.commit()
    for recommandation in recommandations:
        db.refresh(recommandation)
    return recommandations


def _construire_recuperation(
    athlete: Athlete, charge: ChargeResultat, seance_id: uuid.UUID | None
) -> Recommandation:
    contenu = generer_recommandation_recuperation(charge)
    if contenu is None:
        return Recommandation(
            athlete_id=athlete.id,
            type=TypeRecommandation.RECUPERATION,
            seance_declenchante_id=seance_id,
            statut=StatutRecommandation.DONNEES_INSUFFISANTES,
            motif_donnees_insuffisantes="historique de charge insuffisant pour recommander une récupération",
        )
    return Recommandation(
        athlete_id=athlete.id,
        type=TypeRecommandation.RECUPERATION,
        seance_declenchante_id=seance_id,
        statut=StatutRecommandation.DISPONIBLE,
        contenu=contenu,
        justification={
            "ratio_acwr": charge.ratio_acwr,
            "tendance": charge.tendance,
            "charge_aigue_7j": charge.charge_aigue_7j,
        },
    )


def _construire_nutrition(
    athlete: Athlete, charge: ChargeResultat, seance_id: uuid.UUID | None
) -> Recommandation:
    contenu, motif = generer_estimation_nutrition(athlete, charge)
    if contenu is None:
        return Recommandation(
            athlete_id=athlete.id,
            type=TypeRecommandation.NUTRITION,
            seance_declenchante_id=seance_id,
            statut=StatutRecommandation.DONNEES_INSUFFISANTES,
            motif_donnees_insuffisantes=motif,
        )
    return Recommandation(
        athlete_id=athlete.id,
        type=TypeRecommandation.NUTRITION,
        seance_declenchante_id=seance_id,
        statut=StatutRecommandation.DISPONIBLE,
        contenu=contenu,
        justification={
            "poids_kg": float(athlete.poids_kg) if athlete.poids_kg is not None else None,
            "charge_aigue_7j": charge.charge_aigue_7j,
        },
    )
