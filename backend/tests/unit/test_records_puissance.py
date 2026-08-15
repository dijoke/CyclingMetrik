from __future__ import annotations

from src.services.puissance.records import calculer_records_puissance


def test_calculer_records_puissance_avec_flux_absent():
    records = calculer_records_puissance(None)

    assert records.puissance_max_1min is None
    assert records.puissance_max_3min is None
    assert records.puissance_max_5min is None
    assert records.puissance_max_10min is None
    assert records.puissance_max_20min is None


def test_calculer_records_puissance_puissance_constante():
    watts = [200] * (25 * 60)  # 25 minutes à 200W constant

    records = calculer_records_puissance(watts)

    assert records.puissance_max_1min == 200
    assert records.puissance_max_3min == 200
    assert records.puissance_max_5min == 200
    assert records.puissance_max_10min == 200
    assert records.puissance_max_20min == 200


def test_calculer_records_puissance_identifie_le_meilleur_effort():
    # 30 minutes à 100W, avec un pic de 5 minutes à 300W au milieu.
    watts = [100] * (12 * 60) + [300] * (5 * 60) + [100] * (13 * 60)

    records = calculer_records_puissance(watts)

    assert records.puissance_max_1min == 300
    assert records.puissance_max_5min == 300
    # Sur 10 min, la meilleure fenêtre mélange forcément une partie du pic et du plat.
    assert 100 < records.puissance_max_10min < 300
    assert records.puissance_max_20min is not None


def test_calculer_records_puissance_seance_trop_courte_pour_certaines_durees():
    watts = [150] * (7 * 60)  # 7 minutes seulement

    records = calculer_records_puissance(watts)

    assert records.puissance_max_1min == 150
    assert records.puissance_max_3min == 150
    assert records.puissance_max_5min == 150
    assert records.puissance_max_10min is None
    assert records.puissance_max_20min is None


def test_calculer_records_puissance_flux_vide():
    records = calculer_records_puissance([])

    assert records.puissance_max_1min is None
    assert records.puissance_max_20min is None
