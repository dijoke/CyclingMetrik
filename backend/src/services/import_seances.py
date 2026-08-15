from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from src.integrations.base import PlateformeConnecteur, SeanceBrute, TokensOAuth
from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme
from src.models.seance import Seance, StatutDonneesSeance
from src.security.token_crypto import dechiffrer

FC_MIN_PLAUSIBLE = 30
FC_MAX_PLAUSIBLE = 240
VITESSE_MAX_PLAUSIBLE_MS = 25  # ~90 km/h, généreux pour vélo + forte descente
IMPORT_INITIAL_JOURS = 30  # 1ère synchronisation Garmin/Nolio (Strava importe tout, FR-001/004)


def tokens_depuis_connexion(connexion: ConnexionPlateforme) -> TokensOAuth:
    return TokensOAuth(
        access_token=dechiffrer(connexion.access_token_chiffre),
        refresh_token=(
            dechiffrer(connexion.refresh_token_chiffre) if connexion.refresh_token_chiffre else None
        ),
        expire_le=connexion.date_expiration_token,
    )


def _statut_donnees(brute: SeanceBrute) -> StatutDonneesSeance:
    """Marque une séance `aberrant` si ses métriques sortent d'une plage physiologique plausible."""
    if brute.frequence_cardiaque_moyenne is not None and not (
        FC_MIN_PLAUSIBLE <= brute.frequence_cardiaque_moyenne <= FC_MAX_PLAUSIBLE
    ):
        return StatutDonneesSeance.ABERRANT
    if brute.distance_metres and brute.duree_secondes:
        vitesse = brute.distance_metres / brute.duree_secondes
        if vitesse > VITESSE_MAX_PLAUSIBLE_MS:
            return StatutDonneesSeance.ABERRANT
    return StatutDonneesSeance.VALIDE


def importer_seances(
    db: Session,
    connexion: ConnexionPlateforme,
    connecteur: PlateformeConnecteur,
) -> list[Seance]:
    if connexion.date_derniere_synchronisation is not None:
        depuis: datetime | None = connexion.date_derniere_synchronisation
    elif connexion.plateforme == Plateforme.STRAVA:
        depuis = None  # 1ère synchronisation Strava : historique complet (FR-001)
    else:
        depuis = datetime.now(UTC) - timedelta(days=IMPORT_INITIAL_JOURS)

    tokens = tokens_depuis_connexion(connexion)
    seances_brutes = connecteur.recuperer_seances(tokens, depuis)

    seances_importees: list[Seance] = []
    for brute in seances_brutes:
        existe = (
            db.query(Seance)
            .filter_by(connexion_plateforme_id=connexion.id, id_externe=brute.id_externe)
            .first()
        )
        if existe is not None:
            continue

        seance = Seance(
            athlete_id=connexion.athlete_id,
            connexion_plateforme_id=connexion.id,
            id_externe=brute.id_externe,
            date_debut=brute.date_debut,
            duree_secondes=brute.duree_secondes,
            distance_metres=brute.distance_metres,
            puissance_moyenne_watts=brute.puissance_moyenne_watts,
            frequence_cardiaque_moyenne=brute.frequence_cardiaque_moyenne,
            denivele_metres=brute.denivele_metres,
            statut_donnees=_statut_donnees(brute),
        )
        db.add(seance)
        seances_importees.append(seance)

    connexion.date_derniere_synchronisation = datetime.now(UTC)
    db.commit()
    for seance in seances_importees:
        db.refresh(seance)
    return seances_importees
