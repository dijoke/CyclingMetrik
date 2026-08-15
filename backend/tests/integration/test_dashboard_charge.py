from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme
from src.models.seance import Seance, StatutDonneesSeance


def _seance(db, athlete, connexion, jours_avant, puissance=250, duree_h=3):
    db.add(
        Seance(
            athlete_id=athlete.id,
            connexion_plateforme_id=connexion.id,
            id_externe=str(uuid.uuid4()),
            date_debut=datetime.now(UTC) - timedelta(days=jours_avant),
            duree_secondes=int(duree_h * 3600),
            puissance_moyenne_watts=puissance,
            statut_donnees=StatutDonneesSeance.VALIDE,
        )
    )
    db.commit()


def test_surcharge_affichee_apres_forte_hausse(client, db, athlete):
    """US2 Acceptance Scenario 2 : signal de surcharge si forte hausse récente."""
    connexion = ConnexionPlateforme(
        athlete_id=athlete.id, plateforme=Plateforme.STRAVA, access_token_chiffre=b"x"
    )
    db.add(connexion)
    db.commit()

    for jour in range(20, 28):
        _seance(db, athlete, connexion, jour, puissance=100, duree_h=0.5)
    for jour in range(0, 6):
        _seance(db, athlete, connexion, jour, puissance=250, duree_h=3)

    reponse = client.get("/api/dashboard/charge")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["donnees_suffisantes"] is True
    assert corps["tendance"] == "surcharge"


def test_donnees_insuffisantes_sans_historique(client):
    """US2 Acceptance Scenario 3 : jamais d'analyse trompeuse sans données suffisantes."""
    reponse = client.get("/api/dashboard/charge")

    corps = reponse.json()
    assert corps["donnees_suffisantes"] is False
    assert corps["tendance"] is None
