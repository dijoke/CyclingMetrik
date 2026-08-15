from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx

from src.config import get_settings
from src.integrations.base import (
    PlateformeIndisponibleError,
    SeanceBrute,
    TokenInvalideError,
    TokensOAuth,
)

# NOTE (research.md §2) : endpoints Nolio illustratifs, à confirmer avec la documentation
# officielle avant intégration réelle. Respecte l'interface commune PlateformeConnecteur ;
# ajustable sans impact sur le reste du système (research.md §2, alternative écartée).
AUTORISATION_URL = "https://id.nolio.cc/oauth/authorize"
TOKEN_URL = "https://id.nolio.cc/oauth/token"
ACTIVITES_URL = "https://api.nolio.cc/v1/activities"


class NolioConnecteur:
    def url_autorisation(self, redirect_uri: str, state: str) -> str:
        params = httpx.QueryParams(
            {
                "client_id": get_settings().nolio_client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "state": state,
            }
        )
        return f"{AUTORISATION_URL}?{params}"

    def echanger_code(self, code: str, redirect_uri: str) -> TokensOAuth:
        reponse = httpx.post(
            TOKEN_URL,
            data={
                "client_id": get_settings().nolio_client_id,
                "client_secret": get_settings().nolio_client_secret,
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
                "client_id": get_settings().nolio_client_id,
                "client_secret": get_settings().nolio_client_secret,
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
                params={"since": depuis.isoformat()},
            )
        except httpx.TransportError as exc:
            raise PlateformeIndisponibleError("Nolio API injoignable") from exc

        if reponse.status_code == 401:
            raise TokenInvalideError("Token Nolio refusé")
        if reponse.status_code >= 500:
            raise PlateformeIndisponibleError(f"Nolio API indisponible ({reponse.status_code})")
        reponse.raise_for_status()

        return [self._seance_depuis_activite(a) for a in reponse.json().get("activities", [])]

    def revoquer(self, tokens: TokensOAuth) -> None:
        httpx.post(f"{TOKEN_URL}/revoke", data={"token": tokens.access_token})

    @staticmethod
    def _tokens_depuis_reponse(reponse: httpx.Response) -> TokensOAuth:
        if reponse.status_code == 401:
            raise TokenInvalideError("Token Nolio refusé")
        if reponse.status_code >= 500:
            raise PlateformeIndisponibleError(f"Nolio API indisponible ({reponse.status_code})")
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
            id_externe=str(activite["id"]),
            date_debut=datetime.fromisoformat(activite["startedAt"]),
            duree_secondes=activite["durationSeconds"],
            distance_metres=activite.get("distanceMeters"),
            puissance_moyenne_watts=activite.get("avgPowerWatts"),
            frequence_cardiaque_moyenne=activite.get("avgHeartRate"),
            denivele_metres=activite.get("elevationGainMeters"),
        )
