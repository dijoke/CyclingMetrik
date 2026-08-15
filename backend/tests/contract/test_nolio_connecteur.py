from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from src.integrations.base import PlateformeIndisponibleError, TokenInvalideError, TokensOAuth
from src.integrations.nolio.connecteur import NolioConnecteur

FIXTURES = Path(__file__).parent / "fixtures" / "nolio"


def _charger(nom: str) -> dict:
    return json.loads((FIXTURES / nom).read_text())


def _reponse(status_code: int, data: dict | list) -> httpx.Response:
    return httpx.Response(status_code, json=data, request=httpx.Request("GET", "http://x"))


def test_echanger_code_normalise_les_tokens(monkeypatch):
    data = _charger("token_succes.json")
    monkeypatch.setattr(httpx, "post", lambda *a, **k: _reponse(200, data))

    tokens = NolioConnecteur().echanger_code("code", "http://redirect")

    assert tokens.access_token == data["access_token"]
    assert tokens.refresh_token == data["refresh_token"]
    assert tokens.expire_le is not None


def test_recuperer_seances_normalise_en_seance_brute(monkeypatch):
    data = _charger("activites_succes.json")
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(200, data))

    seances = NolioConnecteur().recuperer_seances(
        TokensOAuth("t", None, None), datetime.now(UTC)
    )

    activite = data["activities"][0]
    assert len(seances) == 1
    assert seances[0].id_externe == activite["id"]
    assert seances[0].duree_secondes == activite["durationSeconds"]
    assert seances[0].puissance_moyenne_watts == activite["avgPowerWatts"]


def test_token_expire_leve_erreur_dediee(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(401, {}))

    with pytest.raises(TokenInvalideError):
        NolioConnecteur().recuperer_seances(TokensOAuth("t", None, None), datetime.now(UTC))


def test_plateforme_indisponible_leve_erreur_dediee(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(503, {}))

    with pytest.raises(PlateformeIndisponibleError):
        NolioConnecteur().recuperer_seances(TokensOAuth("t", None, None), datetime.now(UTC))
