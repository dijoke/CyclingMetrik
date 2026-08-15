from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme
from src.models.seance import Seance, StatutDonneesSeance
from src.services.statistiques.agregats import (
    comparaison_annuelle,
    records_personnels,
    statistiques_annuelles,
    statistiques_mensuelles,
)


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
    date_debut,
    duree_h=1,
    distance_km=30,
    denivele=200,
    puissance=None,
    statut=StatutDonneesSeance.VALIDE,
):
    seance = Seance(
        athlete_id=athlete.id,
        connexion_plateforme_id=connexion.id,
        id_externe=str(uuid.uuid4()),
        date_debut=date_debut,
        duree_secondes=int(duree_h * 3600),
        distance_metres=distance_km * 1000,
        denivele_metres=denivele,
        puissance_moyenne_watts=puissance,
        statut_donnees=statut,
    )
    db.add(seance)
    db.commit()
    return seance


def test_statistiques_annuelles_agrege_par_annee_et_exclut_donnees_invalides(db, athlete):
    connexion = _connexion(db, athlete)
    _ajouter_seance(db, athlete, connexion, datetime(2024, 3, 1, tzinfo=UTC), distance_km=20)
    _ajouter_seance(db, athlete, connexion, datetime(2024, 6, 1, tzinfo=UTC), distance_km=30)
    _ajouter_seance(db, athlete, connexion, datetime(2025, 1, 15, tzinfo=UTC), distance_km=40)
    _ajouter_seance(
        db,
        athlete,
        connexion,
        datetime(2024, 7, 1, tzinfo=UTC),
        distance_km=999,
        statut=StatutDonneesSeance.ABERRANT,
    )

    stats = statistiques_annuelles(db, athlete.id)
    par_annee = {s.annee: s for s in stats}

    assert par_annee[2024].nb_seances == 2
    assert par_annee[2024].distance_metres == 50_000
    assert par_annee[2025].nb_seances == 1
    assert par_annee[2025].distance_metres == 40_000


def test_statistiques_mensuelles_agrege_par_mois_pour_une_annee(db, athlete):
    connexion = _connexion(db, athlete)
    _ajouter_seance(db, athlete, connexion, datetime(2024, 3, 1, tzinfo=UTC), distance_km=20)
    _ajouter_seance(db, athlete, connexion, datetime(2024, 3, 15, tzinfo=UTC), distance_km=10)
    _ajouter_seance(db, athlete, connexion, datetime(2024, 6, 1, tzinfo=UTC), distance_km=30)
    _ajouter_seance(db, athlete, connexion, datetime(2025, 3, 1, tzinfo=UTC), distance_km=999)

    stats = statistiques_mensuelles(db, athlete.id, 2024)
    par_mois = {s.mois: s for s in stats}

    assert par_mois[3].nb_seances == 2
    assert par_mois[3].distance_metres == 30_000
    assert par_mois[6].nb_seances == 1
    assert sum(s.nb_seances for s in stats) == 3  # la séance de 2025 est exclue


def test_records_personnels_identifie_les_bonnes_seances(db, athlete):
    connexion = _connexion(db, athlete)
    _ajouter_seance(db, athlete, connexion, datetime(2024, 1, 1, tzinfo=UTC), distance_km=50, denivele=500)
    plus_longue = _ajouter_seance(
        db, athlete, connexion, datetime(2024, 2, 1, tzinfo=UTC), distance_km=150, denivele=800
    )
    plus_de_denivele = _ajouter_seance(
        db, athlete, connexion, datetime(2024, 3, 1, tzinfo=UTC), distance_km=80, denivele=2500
    )

    records = records_personnels(db, athlete.id)

    assert records.plus_longue_distance.date_debut == plus_longue.date_debut
    assert records.plus_de_denivele.date_debut == plus_de_denivele.date_debut
    assert records.puissance_moyenne_max is None


def test_records_personnels_puissance_max_quand_renseignee(db, athlete):
    connexion = _connexion(db, athlete)
    _ajouter_seance(db, athlete, connexion, datetime(2024, 1, 1, tzinfo=UTC), puissance=180)
    plus_puissante = _ajouter_seance(
        db, athlete, connexion, datetime(2024, 2, 1, tzinfo=UTC), puissance=250
    )

    records = records_personnels(db, athlete.id)

    assert records.puissance_moyenne_max.date_debut == plus_puissante.date_debut


def test_comparaison_annuelle_sans_donnees_annee_precedente(db, athlete):
    connexion = _connexion(db, athlete)
    maintenant = datetime.now(UTC)
    _ajouter_seance(db, athlete, connexion, maintenant.replace(month=1, day=2), distance_km=20)

    comparaison = comparaison_annuelle(db, athlete.id, maintenant)

    assert comparaison.annee_courante.nb_seances == 1
    assert comparaison.annee_precedente is None


def test_comparaison_annuelle_avec_donnees_deux_annees(db, athlete):
    connexion = _connexion(db, athlete)
    maintenant = datetime(2025, 6, 15, tzinfo=UTC)
    _ajouter_seance(db, athlete, connexion, datetime(2025, 3, 1, tzinfo=UTC), distance_km=20)
    _ajouter_seance(db, athlete, connexion, datetime(2024, 3, 1, tzinfo=UTC), distance_km=15)
    # Hors période de comparaison (après le 15 juin de l'année précédente) — ne doit pas compter.
    _ajouter_seance(db, athlete, connexion, datetime(2024, 8, 1, tzinfo=UTC), distance_km=999)

    comparaison = comparaison_annuelle(db, athlete.id, maintenant)

    assert comparaison.annee_courante.distance_metres == 20_000
    assert comparaison.annee_precedente is not None
    assert comparaison.annee_precedente.distance_metres == 15_000
