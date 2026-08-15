from __future__ import annotations

from src.models.athlete import Athlete
from src.services.recommendations.nutrition import (
    GRAMMES_PROTEINES_PAR_KG,
    KCAL_PAR_KG_BASE,
    generer_estimation_nutrition,
)
from src.services.training_load.calcul_charge import ChargeResultat


def _charge(aigue: float = 500.0, suffisant: bool = True) -> ChargeResultat:
    return ChargeResultat(
        date_calcul=None,  # type: ignore[arg-type]
        charge_aigue_7j=aigue,
        charge_chronique_28j=aigue,
        ratio_acwr=1.0,
        tendance="stable",
        donnees_suffisantes=suffisant,
    )


def test_insuffisant_si_poids_manquant():
    athlete = Athlete(email="x@example.com", poids_kg=None)

    contenu, motif = generer_estimation_nutrition(athlete, _charge())

    assert contenu is None
    assert motif is not None and "poids" in motif


def test_insuffisant_si_charge_non_calculable():
    athlete = Athlete(email="x@example.com", poids_kg=70)

    contenu, motif = generer_estimation_nutrition(athlete, _charge(suffisant=False))

    assert contenu is None
    assert motif is not None


def test_estimation_disponible_et_coherente():
    athlete = Athlete(email="x@example.com", poids_kg=70)

    contenu, motif = generer_estimation_nutrition(athlete, _charge(aigue=1000.0))

    assert motif is None
    assert contenu is not None
    assert contenu["calories_kcal"] > 70 * KCAL_PAR_KG_BASE
    assert contenu["glucides_g"] > 0
    assert contenu["proteines_g"] == round(70 * GRAMMES_PROTEINES_PAR_KG)
    assert contenu["lipides_g"] >= 0
