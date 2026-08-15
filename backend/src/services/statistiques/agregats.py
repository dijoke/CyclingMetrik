from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import extract, func
from sqlalchemy.orm import Query, Session

from src.models.seance import Seance, StatutDonneesSeance


@dataclass
class StatPeriode:
    distance_metres: float
    denivele_metres: float
    duree_secondes: int
    nb_seances: int


@dataclass
class StatAnnuelle(StatPeriode):
    annee: int


@dataclass
class StatMensuelle(StatPeriode):
    mois: int


@dataclass
class SeanceResume:
    date_debut: datetime
    distance_metres: float | None
    denivele_metres: float | None
    duree_secondes: int
    puissance_moyenne_watts: float | None


@dataclass
class RecordsPersonnels:
    plus_longue_distance: SeanceResume | None
    plus_de_denivele: SeanceResume | None
    plus_longue_duree: SeanceResume | None
    puissance_moyenne_max: SeanceResume | None


@dataclass
class ComparaisonAnnuelle:
    annee_courante: StatAnnuelle
    annee_precedente: StatAnnuelle | None


def _seances_valides(db: Session, athlete_id: uuid.UUID) -> Query:
    """Séances comptant pour les statistiques : exclut aberrant/doublon_probable (FR-004)."""
    return db.query(Seance).filter(
        Seance.athlete_id == athlete_id,
        Seance.statut_donnees == StatutDonneesSeance.VALIDE,
    )


def statistiques_annuelles(db: Session, athlete_id: uuid.UUID) -> list[StatAnnuelle]:
    annee_col = extract("year", Seance.date_debut)
    lignes = (
        _seances_valides(db, athlete_id)
        .with_entities(
            annee_col.label("annee"),
            func.coalesce(func.sum(Seance.distance_metres), 0).label("distance_metres"),
            func.coalesce(func.sum(Seance.denivele_metres), 0).label("denivele_metres"),
            func.sum(Seance.duree_secondes).label("duree_secondes"),
            func.count(Seance.id).label("nb_seances"),
        )
        .group_by(annee_col)
        .order_by(annee_col)
        .all()
    )
    return [
        StatAnnuelle(
            annee=int(ligne.annee),
            distance_metres=float(ligne.distance_metres),
            denivele_metres=float(ligne.denivele_metres),
            duree_secondes=int(ligne.duree_secondes),
            nb_seances=ligne.nb_seances,
        )
        for ligne in lignes
    ]


def statistiques_mensuelles(db: Session, athlete_id: uuid.UUID, annee: int) -> list[StatMensuelle]:
    mois_col = extract("month", Seance.date_debut)
    lignes = (
        _seances_valides(db, athlete_id)
        .filter(extract("year", Seance.date_debut) == annee)
        .with_entities(
            mois_col.label("mois"),
            func.coalesce(func.sum(Seance.distance_metres), 0).label("distance_metres"),
            func.coalesce(func.sum(Seance.denivele_metres), 0).label("denivele_metres"),
            func.sum(Seance.duree_secondes).label("duree_secondes"),
            func.count(Seance.id).label("nb_seances"),
        )
        .group_by(mois_col)
        .order_by(mois_col)
        .all()
    )
    return [
        StatMensuelle(
            mois=int(ligne.mois),
            distance_metres=float(ligne.distance_metres),
            denivele_metres=float(ligne.denivele_metres),
            duree_secondes=int(ligne.duree_secondes),
            nb_seances=ligne.nb_seances,
        )
        for ligne in lignes
    ]


def _resume(seance: Seance | None) -> SeanceResume | None:
    if seance is None:
        return None
    return SeanceResume(
        date_debut=seance.date_debut,
        distance_metres=float(seance.distance_metres) if seance.distance_metres is not None else None,
        denivele_metres=float(seance.denivele_metres) if seance.denivele_metres is not None else None,
        duree_secondes=seance.duree_secondes,
        puissance_moyenne_watts=(
            float(seance.puissance_moyenne_watts) if seance.puissance_moyenne_watts is not None else None
        ),
    )


def records_personnels(db: Session, athlete_id: uuid.UUID) -> RecordsPersonnels:
    base = _seances_valides(db, athlete_id)
    return RecordsPersonnels(
        plus_longue_distance=_resume(
            base.filter(Seance.distance_metres.is_not(None))
            .order_by(Seance.distance_metres.desc())
            .first()
        ),
        plus_de_denivele=_resume(
            base.filter(Seance.denivele_metres.is_not(None))
            .order_by(Seance.denivele_metres.desc())
            .first()
        ),
        plus_longue_duree=_resume(base.order_by(Seance.duree_secondes.desc()).first()),
        puissance_moyenne_max=_resume(
            base.filter(Seance.puissance_moyenne_watts.is_not(None))
            .order_by(Seance.puissance_moyenne_watts.desc())
            .first()
        ),
    )


def _cumul_periode(
    db: Session, athlete_id: uuid.UUID, debut: datetime, fin: datetime, annee: int
) -> StatAnnuelle | None:
    ligne = (
        _seances_valides(db, athlete_id)
        .filter(Seance.date_debut >= debut, Seance.date_debut <= fin)
        .with_entities(
            func.coalesce(func.sum(Seance.distance_metres), 0).label("distance_metres"),
            func.coalesce(func.sum(Seance.denivele_metres), 0).label("denivele_metres"),
            func.coalesce(func.sum(Seance.duree_secondes), 0).label("duree_secondes"),
            func.count(Seance.id).label("nb_seances"),
        )
        .one()
    )
    if ligne.nb_seances == 0:
        return None
    return StatAnnuelle(
        annee=annee,
        distance_metres=float(ligne.distance_metres),
        denivele_metres=float(ligne.denivele_metres),
        duree_secondes=int(ligne.duree_secondes),
        nb_seances=ligne.nb_seances,
    )


def comparaison_annuelle(db: Session, athlete_id: uuid.UUID, maintenant: datetime) -> ComparaisonAnnuelle:
    """Cumul du 1er janvier à `maintenant`, comparé à la même période l'année précédente.
    `annee_precedente` est `None` si l'historique ne couvre pas cette période (FR-006) — distingue
    explicitement "pas de donnée" d'un écart nul trompeur."""
    debut_courante = maintenant.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    courante = _cumul_periode(db, athlete_id, debut_courante, maintenant, maintenant.year) or StatAnnuelle(
        annee=maintenant.year, distance_metres=0.0, denivele_metres=0.0, duree_secondes=0, nb_seances=0
    )

    debut_precedente = debut_courante.replace(year=maintenant.year - 1)
    fin_precedente = maintenant.replace(year=maintenant.year - 1)
    precedente = _cumul_periode(db, athlete_id, debut_precedente, fin_precedente, maintenant.year - 1)

    return ComparaisonAnnuelle(annee_courante=courante, annee_precedente=precedente)
