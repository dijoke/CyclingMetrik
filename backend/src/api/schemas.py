from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.models.connexion_plateforme import Plateforme, StatutConnexion
from src.models.recommandation import StatutRecommandation, TypeRecommandation
from src.models.seance import StatutDonneesSeance


class ConnexionPlateformeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plateforme: Plateforme
    statut: StatutConnexion
    date_derniere_synchronisation: datetime | None
    date_connexion: datetime


class SeanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    date_debut: datetime
    duree_secondes: int
    distance_metres: float | None
    puissance_moyenne_watts: float | None
    frequence_cardiaque_moyenne: int | None
    denivele_metres: float | None
    statut_donnees: StatutDonneesSeance
    seance_doublon_de_id: uuid.UUID | None
    puissance_max_1min: float | None
    puissance_max_3min: float | None
    puissance_max_5min: float | None
    puissance_max_10min: float | None
    puissance_max_20min: float | None


class PointChargeHistoriqueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: datetime
    charge_aigue_7j: float | None
    charge_chronique_28j: float | None


class ChargeEntrainementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date_calcul: datetime
    charge_aigue_7j: float | None
    charge_chronique_28j: float | None
    ratio_acwr: float | None
    tendance: str | None
    donnees_suffisantes: bool
    historique: list[PointChargeHistoriqueOut]


class RecommandationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: TypeRecommandation
    date_generation: datetime
    statut: StatutRecommandation
    contenu: dict | None
    motif_donnees_insuffisantes: str | None
    justification: dict | None


class AthleteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    poids_kg: float | None
    taille_cm: int | None
    objectifs: str | None
    contraintes_alimentaires: list[str]


class AthleteProfilInput(BaseModel):
    poids_kg: float | None = None
    taille_cm: int | None = None
    objectifs: str | None = None
    contraintes_alimentaires: list[str] | None = None


class StatAnnuelleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    annee: int
    distance_metres: float
    denivele_metres: float
    duree_secondes: int
    nb_seances: int


class StatMensuelleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mois: int
    distance_metres: float
    denivele_metres: float
    duree_secondes: int
    nb_seances: int


class SeanceResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date_debut: datetime
    distance_metres: float | None
    denivele_metres: float | None
    duree_secondes: int
    puissance_moyenne_watts: float | None


class RecordsPersonnelsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plus_longue_distance: SeanceResumeOut | None
    plus_de_denivele: SeanceResumeOut | None
    plus_longue_duree: SeanceResumeOut | None
    puissance_moyenne_max: SeanceResumeOut | None


class ComparaisonAnnuelleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    annee_courante: StatAnnuelleOut
    annee_precedente: StatAnnuelleOut | None


class AutorisationOut(BaseModel):
    url_autorisation: str


class CallbackInput(BaseModel):
    code: str
