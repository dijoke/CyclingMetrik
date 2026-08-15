from __future__ import annotations

from datetime import UTC, datetime

from src.api.connexions import CONNECTEURS
from src.integrations.base import SeanceBrute, TokensOAuth
from src.models.connexion_plateforme import Plateforme


def test_connexion_et_import_initial(client, monkeypatch):
    """quickstart.md §US1 étapes 1-4 : connecter, autoriser, importer les séances récentes."""
    connecteur = CONNECTEURS[Plateforme.STRAVA]
    monkeypatch.setattr(
        connecteur, "echanger_code", lambda code, redirect_uri: TokensOAuth("acc", "ref", None)
    )
    monkeypatch.setattr(
        connecteur,
        "recuperer_seances",
        lambda tokens, depuis: [
            SeanceBrute(
                id_externe="ext-1",
                date_debut=datetime.now(UTC),
                duree_secondes=3600,
                puissance_moyenne_watts=200,
            )
        ],
    )

    reponse_connexion = client.post("/api/connexions/strava/callback", json={"code": "abc"})
    assert reponse_connexion.status_code == 201
    assert reponse_connexion.json()["statut"] == "actif"

    reponse_seances = client.get("/api/seances")
    assert reponse_seances.status_code == 200
    seances = reponse_seances.json()
    assert len(seances) == 1
    assert seances[0]["duree_secondes"] == 3600
    assert seances[0]["statut_donnees"] == "valide"


def test_seance_deja_importee_non_dupliquee(client, monkeypatch):
    connecteur = CONNECTEURS[Plateforme.STRAVA]
    monkeypatch.setattr(
        connecteur, "echanger_code", lambda code, redirect_uri: TokensOAuth("acc", "ref", None)
    )
    seance_brute = [
        SeanceBrute(
            id_externe="ext-1", date_debut=datetime.now(UTC), duree_secondes=3600
        )
    ]
    monkeypatch.setattr(connecteur, "recuperer_seances", lambda tokens, depuis: seance_brute)

    client.post("/api/connexions/strava/callback", json={"code": "abc"})
    client.post("/api/connexions/strava/callback", json={"code": "abc"})

    reponse_seances = client.get("/api/seances")
    assert len(reponse_seances.json()) == 1
