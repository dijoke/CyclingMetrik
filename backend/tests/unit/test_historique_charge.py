from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme
from src.models.seance import Seance, StatutDonneesSeance
from src.services.training_load.calcul_charge import calculer_charge, historique_charge


def _connexion(db, athlete):
    connexion = ConnexionPlateforme(
        athlete_id=athlete.id, plateforme=Plateforme.STRAVA, access_token_chiffre=b"x"
    )
    db.add(connexion)
    db.commit()
    db.refresh(connexion)
    return connexion


def _ajouter_seance(
    db,
    athlete,
    connexion,
    jours_avant,
    duree_h=1,
    puissance=200,
    statut=StatutDonneesSeance.VALIDE,
):
    seance = Seance(
        athlete_id=athlete.id,
        connexion_plateforme_id=connexion.id,
        id_externe=str(uuid.uuid4()),
        date_debut=datetime.now(UTC) - timedelta(days=jours_avant),
        duree_secondes=int(duree_h * 3600),
        puissance_moyenne_watts=puissance,
        statut_donnees=statut,
    )
    db.add(seance)
    db.commit()
    return seance


def test_historique_vide_si_donnees_insuffisantes(db, athlete):
    connexion = _connexion(db, athlete)
    _ajouter_seance(db, athlete, connexion, jours_avant=1)

    historique = historique_charge(db, athlete.id)

    assert historique == []


def test_historique_contient_plusieurs_points_ordonnes(db, athlete):
    connexion = _connexion(db, athlete)
    for jour in range(0, 70, 3):
        _ajouter_seance(db, athlete, connexion, jours_avant=jour, duree_h=1, puissance=200)

    historique = historique_charge(db, athlete.id)

    assert len(historique) == 8
    dates = [point.date for point in historique]
    assert dates == sorted(dates)
    # Pas une simple répétition du même instantané : au moins deux dates distinctes.
    assert len(set(dates)) > 1


def test_dernier_point_historique_coherent_avec_calcul_courant(db, athlete):
    connexion = _connexion(db, athlete)
    for jour in range(0, 70, 3):
        _ajouter_seance(db, athlete, connexion, jours_avant=jour, duree_h=1, puissance=200)

    resultat_courant = calculer_charge(db, athlete.id)
    historique = historique_charge(db, athlete.id)

    dernier_point = historique[-1]
    assert dernier_point.charge_aigue_7j == resultat_courant.charge_aigue_7j
    assert dernier_point.charge_chronique_28j == resultat_courant.charge_chronique_28j
