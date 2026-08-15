from __future__ import annotations

import json
import time
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


def _activite(id_externe: int) -> dict:
    return {
        "id": id_externe,
        "start_date": "2026-01-01T07:00:00Z",
        "elapsed_time": 3600,
        "distance": 30000.0,
        "average_watts": 200.0,
        "average_heartrate": 140.0,
        "total_elevation_gain": 400.0,
    }


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


def test_recuperer_seances_pagine_sur_plusieurs_pages(monkeypatch):
    page_1 = [_activite(i) for i in range(100)]
    page_2 = [_activite(100)]
    appels: list[int] = []

    def fake_get(url, headers=None, params=None, timeout=None):
        appels.append(params["page"])
        return _reponse(200, page_1 if params["page"] == 1 else page_2)

    monkeypatch.setattr(httpx, "get", fake_get)

    seances = StravaConnecteur().recuperer_seances(TokensOAuth("t", None, None), None)

    assert len(seances) == 101
    assert appels == [1, 2]


def test_recuperer_seances_sans_borne_temporelle_omet_after(monkeypatch):
    params_captures = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        params_captures.update(params)
        return _reponse(200, [])

    monkeypatch.setattr(httpx, "get", fake_get)

    StravaConnecteur().recuperer_seances(TokensOAuth("t", None, None), None)

    assert "after" not in params_captures


def test_recuperer_seances_retente_automatiquement_sur_limite_de_debit(monkeypatch):
    appels = {"n": 0}

    def fake_get(url, headers=None, params=None, timeout=None):
        appels["n"] += 1
        if appels["n"] < 3:
            return _reponse(429, {})
        return _reponse(200, [])

    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(time, "sleep", lambda secondes: None)

    seances = StravaConnecteur().recuperer_seances(TokensOAuth("t", None, None), datetime.now(UTC))

    assert seances == []
    assert appels["n"] == 3


def test_recuperer_seances_leve_erreur_si_limite_de_debit_persiste(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(429, {}))
    monkeypatch.setattr(time, "sleep", lambda secondes: None)

    with pytest.raises(PlateformeIndisponibleError):
        StravaConnecteur().recuperer_seances(TokensOAuth("t", None, None), datetime.now(UTC))


def test_recuperer_seances_retente_sur_timeout_transitoire(monkeypatch):
    appels = {"n": 0}

    def fake_get(url, headers=None, params=None, timeout=None):
        appels["n"] += 1
        if appels["n"] < 2:
            raise httpx.ReadTimeout("timed out")
        return _reponse(200, [])

    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(time, "sleep", lambda secondes: None)

    seances = StravaConnecteur().recuperer_seances(TokensOAuth("t", None, None), datetime.now(UTC))

    assert seances == []
    assert appels["n"] == 2


def test_recuperer_flux_puissance_renvoie_les_watts(monkeypatch):
    donnees = {"watts": {"data": [100, 150, 200], "series_type": "time"}}
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(200, donnees))

    flux = StravaConnecteur().recuperer_flux_puissance(TokensOAuth("t", None, None), "12345")

    assert flux == [100, 150, 200]


def test_recuperer_flux_puissance_absent_si_pas_de_capteur(monkeypatch):
    donnees = {"time": {"data": [0, 1, 2], "series_type": "time"}}  # pas de clé "watts"
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(200, donnees))

    flux = StravaConnecteur().recuperer_flux_puissance(TokensOAuth("t", None, None), "12345")

    assert flux is None


def test_recuperer_flux_puissance_absent_si_404(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _reponse(404, {}))

    flux = StravaConnecteur().recuperer_flux_puissance(TokensOAuth("t", None, None), "12345")

    assert flux is None
