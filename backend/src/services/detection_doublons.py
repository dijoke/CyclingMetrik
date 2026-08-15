from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from src.models.seance import Seance, StatutDonneesSeance

FENETRE_DATE = timedelta(minutes=5)
TOLERANCE_DUREE = 0.02  # ±2 %


def detecter_doublons(db: Session, athlete_id: uuid.UUID) -> list[Seance]:
    """Marque (sans fusionner) les séances probablement dupliquées entre plateformes.

    research.md §7 : la fusion automatique est écartée (risque de perte de données) ;
    l'athlète garde le contrôle, cohérent avec le Principe I (pas de décision silencieuse
    sur des données ambiguës).
    """
    seances = (
        db.query(Seance)
        .filter(
            Seance.athlete_id == athlete_id,
            Seance.statut_donnees != StatutDonneesSeance.DOUBLON_PROBABLE,
        )
        .order_by(Seance.date_debut)
        .all()
    )

    marquees: list[Seance] = []
    for i, seance in enumerate(seances):
        for autre in seances[i + 1 :]:
            if autre.date_debut - seance.date_debut > FENETRE_DATE:
                break
            if autre.connexion_plateforme_id == seance.connexion_plateforme_id:
                continue
            ecart_duree = abs(autre.duree_secondes - seance.duree_secondes) / max(
                seance.duree_secondes, 1
            )
            if ecart_duree <= TOLERANCE_DUREE:
                autre.statut_donnees = StatutDonneesSeance.DOUBLON_PROBABLE
                autre.seance_doublon_de_id = seance.id
                marquees.append(autre)

    db.commit()
    return marquees
