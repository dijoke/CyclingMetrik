from __future__ import annotations

from src.api.connexions import CONNECTEURS
from src.integrations.base import TokenInvalideError
from src.jobs.sync_seances import synchroniser_toutes_connexions
from src.models.connexion_plateforme import ConnexionPlateforme, Plateforme, StatutConnexion
from src.security.token_crypto import chiffrer


def _leve_token_invalide(*args, **kwargs):
    raise TokenInvalideError("refusé")


def test_token_invalide_marque_la_connexion_expiree(db, athlete, monkeypatch):
    """FR-009 : une connexion dont le token est refusé passe en statut `expire`."""
    connexion = ConnexionPlateforme(
        athlete_id=athlete.id,
        plateforme=Plateforme.STRAVA,
        statut=StatutConnexion.ACTIF,
        access_token_chiffre=chiffrer("acc"),
    )
    db.add(connexion)
    db.commit()

    connecteur = CONNECTEURS[Plateforme.STRAVA]
    monkeypatch.setattr(connecteur, "recuperer_seances", _leve_token_invalide)

    synchroniser_toutes_connexions()

    db.refresh(connexion)
    assert connexion.statut == StatutConnexion.EXPIRE
