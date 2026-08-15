from __future__ import annotations


def test_dashboard_charge_respecte_le_contrat(client):
    reponse = client.get("/api/dashboard/charge")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert set(corps.keys()) >= {
        "date_calcul",
        "charge_aigue_7j",
        "charge_chronique_28j",
        "ratio_acwr",
        "tendance",
        "donnees_suffisantes",
    }
    assert corps["donnees_suffisantes"] is False
    assert corps["tendance"] is None
