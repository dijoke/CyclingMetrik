from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme
from src.models.recommandation import StatutRecommandation
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


def _seance(db, athlete, connexion, jours_avant=1):
    seance = Seance(
        athlete_id=athlete.id,
        connexion_plateforme_id=connexion.id,
        id_externe=str(uuid.uuid4()),
        date_debut=datetime.now(UTC) - timedelta(days=jours_avant),
        duree_secondes=3600,
        puissance_moyenne_watts=220,
        statut_donnees=StatutDonneesSeance.VALIDE,
    )
    db.add(seance)
    db.commit()
    db.refresh(seance)
    return seance


def test_invariant_donnees_insuffisantes_sans_historique_de_charge(db, athlete):
    """Principe I (NON-NEGOTIABLE) : pas de contenu ni de statut disponible sans données."""
    connexion = _connexion(db, athlete)
    seance = _seance(db, athlete, connexion)

    recommandations = generer_recommandations(db, athlete, seance_declenchante_id=seance.id)

    for recommandation in recommandations:
        assert recommandation.statut == StatutRecommandation.DONNEES_INSUFFISANTES
        assert recommandation.contenu is None
        assert recommandation.motif_donnees_insuffisantes is not None
        assert recommandation.justification is None


def test_invariant_disponible_avec_profil_et_historique_complets(db, athlete):
    athlete.poids_kg = 70
    db.commit()
    connexion = _connexion(db, athlete)
    for jour in range(1, 20):
        _seance(db, athlete, connexion, jours_avant=jour)
    seance_declenchante = _seance(db, athlete, connexion, jours_avant=0)

    recommandations = generer_recommandations(
        db, athlete, seance_declenchante_id=seance_declenchante.id
    )

    for recommandation in recommandations:
        assert recommandation.statut == StatutRecommandation.DISPONIBLE
        assert recommandation.contenu is not None
        assert recommandation.justification is not None
        assert recommandation.motif_donnees_insuffisantes is None


def test_nutrition_insuffisante_sans_poids_meme_avec_historique(db, athlete):
    connexion = _connexion(db, athlete)
    for jour in range(1, 20):
        _seance(db, athlete, connexion, jours_avant=jour)

    recommandations = generer_recommandations(db, athlete)
    nutrition = next(r for r in recommandations if r.type.value == "nutrition")

    assert nutrition.statut == StatutRecommandation.DONNEES_INSUFFISANTES
    assert nutrition.motif_donnees_insuffisantes is not None
    assert "poids" in nutrition.motif_donnees_insuffisantes
