from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme
from src.models.seance import Seance, StatutDonneesSeance
from src.services.recommendations.moteur import generer_recommandations


def _connexion(db, athlete):
    connexion = ConnexionPlateforme(
        athlete_id=athlete.id, plateforme=Plateforme.STRAVA, access_token_chiffre=b"x"
    )
    db.add(connexion)
    db.commit()
    db.refresh(connexion)
    return connexion


def _seances_historique(db, athlete, connexion):
    for jour in range(1, 20):
        db.add(
            Seance(
                athlete_id=athlete.id,
                connexion_plateforme_id=connexion.id,
                id_externe=str(uuid.uuid4()),
                date_debut=datetime.now(UTC) - timedelta(days=jour),
                duree_secondes=3600,
                puissance_moyenne_watts=200,
                statut_donnees=StatutDonneesSeance.VALIDE,
            )
        )
    db.commit()


def test_recommandation_disponible_avec_profil_complet(client, db, athlete):
    """quickstart.md §US3 étapes 1-4."""
    client.put("/api/athlete/profil", json={"poids_kg": 68})
    connexion = _connexion(db, athlete)
    _seances_historique(db, athlete, connexion)

    db.refresh(athlete)
    generer_recommandations(db, athlete)

    reponse = client.get("/api/recommandations")
    assert reponse.status_code == 200
    recommandations = reponse.json()
    assert len(recommandations) == 2
    for recommandation in recommandations:
        assert recommandation["statut"] == "disponible"
        assert recommandation["contenu"] is not None
        assert recommandation["justification"] is not None


def test_recommandation_nutrition_insuffisante_sans_profil(client, db, athlete):
    """quickstart.md §US3 étapes 5-6 : jamais une estimation nutritionnelle non fondée."""
    connexion = _connexion(db, athlete)
    _seances_historique(db, athlete, connexion)

    generer_recommandations(db, athlete)

    reponse = client.get("/api/recommandations", params={"type": "nutrition"})
    nutrition = reponse.json()[0]
    assert nutrition["statut"] == "donnees_insuffisantes"
    assert nutrition["contenu"] is None
    assert "poids" in nutrition["motif_donnees_insuffisantes"]
