from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme
from src.models.seance import Seance, StatutDonneesSeance
from src.services.training_load.calcul_charge import calculer_charge


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


def test_donnees_insuffisantes_si_historique_court(db, athlete):
    connexion = _connexion(db, athlete)
    _ajouter_seance(db, athlete, connexion, jours_avant=1)

    resultat = calculer_charge(db, athlete.id)

    assert resultat.donnees_suffisantes is False
    assert resultat.tendance is None


def test_tendance_surcharge_si_forte_hausse_recente(db, athlete):
    connexion = _connexion(db, athlete)
    for jour in range(20, 28):
        _ajouter_seance(db, athlete, connexion, jours_avant=jour, duree_h=0.5, puissance=100)
    for jour in range(0, 6):
        _ajouter_seance(db, athlete, connexion, jours_avant=jour, duree_h=3, puissance=250)

    resultat = calculer_charge(db, athlete.id)

    assert resultat.donnees_suffisantes is True
    assert resultat.ratio_acwr > 1.5
    assert resultat.tendance == "surcharge"


def test_tendance_recuperation_si_charge_recente_faible(db, athlete):
    connexion = _connexion(db, athlete)
    for jour in range(15, 28):
        _ajouter_seance(db, athlete, connexion, jours_avant=jour, duree_h=2, puissance=200)

    resultat = calculer_charge(db, athlete.id)

    assert resultat.donnees_suffisantes is True
    assert resultat.tendance == "recuperation"


def test_seances_aberrantes_exclues_du_calcul(db, athlete):
    connexion = _connexion(db, athlete)
    _ajouter_seance(db, athlete, connexion, jours_avant=20)
    _ajouter_seance(
        db,
        athlete,
        connexion,
        jours_avant=1,
        puissance=None,
        statut=StatutDonneesSeance.ABERRANT,
    )

    resultat = calculer_charge(db, athlete.id)

    assert resultat.donnees_suffisantes is True
    assert resultat.charge_aigue_7j == 0
