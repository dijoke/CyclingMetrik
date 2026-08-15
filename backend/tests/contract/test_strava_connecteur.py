from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from src.integrations.base import PlateformeIndisponibleError, TokenInvalideError, TokensOAuth
from src.integrations.strava.connecteur import StravaConnecteur

FIXTURES = Path(__file__).parent / "fixtures" / "strava"


def _charger(nom: str) -> dict:
    return json.loads((FIXTURES / nom).read_text())


def _reponse(status_code: int, data: dict | list) -> httpx.Response:
    return httpx.Response(status_code, json=data, request=httpx.Request("GET", "http://x"))


def test_echanger_code_normalise_les_tokens(monkeypatch):
    data = _charger("token_succes.json")
    monkeypatch.setattr(httpx, "post", lambda *a, **k: _reponse(200, data))

    tokens = StravaConnecteur().echanger_code("code", "http://redirect")

    assert tokens.access_token == data["access_token"]
    assert tokens.refresh_token == data["refresh_token"]
    assert tokens.expire_le == datetime.fromtimestamp(data["expires_at"], tz=UTC)


def test_recuperer_seances_normalise_en_seance_brute(monkeypatch):
    data = _charger("activites_succes.json")
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(200, data))

    seances = StravaConnecteur().recuperer_seances(
        TokensOAuth("t", None, None), datetime.now(UTC)
    )

    assert len(seances) == 2
    assert seances[0].id_externe == str(data[0]["id"])
    assert seances[0].duree_secondes == data[0]["elapsed_time"]
    assert seances[1].puissance_moyenne_watts is None


def test_token_expire_leve_erreur_dediee(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(401, {}))

    with pytest.raises(TokenInvalideError):
        StravaConnecteur().recuperer_seances(TokensOAuth("t", None, None), datetime.now(UTC))


def test_plateforme_indisponible_leve_erreur_dediee(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(503, {}))

    with pytest.raises(PlateformeIndisponibleError):
        StravaConnecteur().recuperer_seances(TokensOAuth("t", None, None), datetime.now(UTC))
