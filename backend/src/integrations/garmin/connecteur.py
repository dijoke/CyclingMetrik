from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import httpx

from src.config import get_settings
from src.integrations.base import (
    PlateformeIndisponibleError,
    SeanceBrute,
    TokenInvalideError,
    TokensOAuth,
)

AUTORISATION_URL = "https://connect.garmin.com/oauth2Confirm"
TOKEN_URL = "https://diauth.garmin.com/di-oauth2-service/oauth/token"
ACTIVITES_URL = "https://apis.garmin.com/wellness-api/rest/activities"

# Stockage en mémoire du code_verifier PKCE le temps du round-trip d'autorisation.
_verifieurs_pkce: dict[str, str] = {}


def _generer_pkce() -> tuple[str, str]:
    verifieur = secrets.token_urlsafe(64)[:128]
    defi = base64.urlsafe_b64encode(hashlib.sha256(verifieur.encode()).digest()).rstrip(b"=").decode()
    return verifieur, defi


class GarminConnecteur:
    def url_autorisation(self, redirect_uri: str, state: str) -> str:
        verifieur, defi = _generer_pkce()
        _verifieurs_pkce[state] = verifieur
        params = httpx.QueryParams(
            {
                "client_id": get_settings().garmin_client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "state": state,
                "code_challenge": defi,
                "code_challenge_method": "S256",
            }
        )
        return f"{AUTORISATION_URL}?{params}"

    def echanger_code(self, code: str, redirect_uri: str) -> TokensOAuth:
        reponse = httpx.post(
            TOKEN_URL,
            data={
                "client_id": get_settings().garmin_client_id,
                "client_secret": get_settings().garmin_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )
        return self._tokens_depuis_reponse(reponse)

    def rafraichir_token(self, refresh_token: str) -> TokensOAuth:
        reponse = httpx.post(
            TOKEN_URL,
            data={
                "client_id": get_settings().garmin_client_id,
                "client_secret": get_settings().garmin_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        return self._tokens_depuis_reponse(reponse)

    def recuperer_seances(self, tokens: TokensOAuth, depuis: datetime) -> list[SeanceBrute]:
        try:
            reponse = httpx.get(
                ACTIVITES_URL,
                headers={"Authorization": f"Bearer {tokens.access_token}"},
                params={
                    "uploadStartTimeInSeconds": int(depuis.timestamp()),
                    "uploadEndTimeInSeconds": int(datetime.now(UTC).timestamp()),
                },
            )
        except httpx.TransportError as exc:
            raise PlateformeIndisponibleError("Garmin Connect API injoignable") from exc

        if reponse.status_code == 401:
            raise TokenInvalideError("Token Garmin Connect refusé")
        if reponse.status_code >= 500:
            raise PlateformeIndisponibleError(f"Garmin Connect API indisponible ({reponse.status_code})")
        reponse.raise_for_status()

        return [self._seance_depuis_activite(a) for a in reponse.json()]

    def revoquer(self, tokens: TokensOAuth) -> None:
        httpx.post(f"{TOKEN_URL}/revoke", data={"token": tokens.access_token})

    @staticmethod
    def _tokens_depuis_reponse(reponse: httpx.Response) -> TokensOAuth:
        if reponse.status_code == 401:
            raise TokenInvalideError("Token Garmin Connect refusé")
        if reponse.status_code >= 500:
            raise PlateformeIndisponibleError(f"Garmin Connect API indisponible ({reponse.status_code})")
        reponse.raise_for_status()
        data = reponse.json()
        expire_le = (
            datetime.now(UTC) + timedelta(seconds=data["expires_in"])
            if "expires_in" in data
            else None
        )
        return TokensOAuth(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expire_le=expire_le,
        )

    @staticmethod
    def _seance_depuis_activite(activite: dict) -> SeanceBrute:
        return SeanceBrute(
            id_externe=str(activite["summaryId"]),
            date_debut=datetime.fromtimestamp(activite["startTimeInSeconds"], tz=UTC),
            duree_secondes=activite["durationInSeconds"],
            distance_metres=activite.get("distanceInMeters"),
            puissance_moyenne_watts=activite.get("averagePowerInWatts"),
            frequence_cardiaque_moyenne=activite.get("averageHeartRateInBeatsPerMinute"),
            denivele_metres=activite.get("totalElevationGainInMeters"),
        )
