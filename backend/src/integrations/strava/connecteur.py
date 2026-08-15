from __future__ import annotations

import time
from datetime import UTC, datetime

import httpx

from src.config import get_settings
from src.integrations.base import (
    PlateformeIndisponibleError,
    SeanceBrute,
    TokenInvalideError,
    TokensOAuth,
)

AUTORISATION_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITES_URL = "https://www.strava.com/api/v3/athlete/activities"
DEAUTHORIZE_URL = "https://www.strava.com/oauth/deauthorize"

PAGE_SIZE = 100
REQUEST_TIMEOUT_SECONDES = 30  # le défaut httpx (5s) est trop court pour /activities en per_page=100
RATE_LIMIT_ATTENTE_SECONDES = 60  # research.md Decision 3
RATE_LIMIT_TENTATIVES_MAX = 16  # ~16 min, couvre la réinitialisation de la fenêtre 15 min de Strava


class StravaConnecteur:
    def url_autorisation(self, redirect_uri: str, state: str) -> str:
        params = httpx.QueryParams(
            {
                "client_id": get_settings().strava_client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "activity:read_all",
                "state": state,
            }
        )
        return f"{AUTORISATION_URL}?{params}"

    def echanger_code(self, code: str, redirect_uri: str) -> TokensOAuth:
        reponse = httpx.post(
            TOKEN_URL,
            data={
                "client_id": get_settings().strava_client_id,
                "client_secret": get_settings().strava_client_secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        return self._tokens_depuis_reponse(reponse)

    def rafraichir_token(self, refresh_token: str) -> TokensOAuth:
        reponse = httpx.post(
            TOKEN_URL,
            data={
                "client_id": get_settings().strava_client_id,
                "client_secret": get_settings().strava_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        return self._tokens_depuis_reponse(reponse)

    def recuperer_seances(self, tokens: TokensOAuth, depuis: datetime | None) -> list[SeanceBrute]:
        """Récupère l'intégralité des activités disponibles (FR-001/FR-002) en paginant tant
        qu'une page renvoie `PAGE_SIZE` résultats. `depuis=None` importe tout l'historique
        (première synchronisation) ; sinon seules les activités après `depuis` sont demandées.
        """
        activites: list[dict] = []
        page = 1
        while True:
            params: dict[str, int] = {"per_page": PAGE_SIZE, "page": page}
            if depuis is not None:
                params["after"] = int(depuis.timestamp())

            reponse = self._get_avec_retry(tokens, params)
            page_activites = reponse.json()
            activites.extend(page_activites)

            if len(page_activites) < PAGE_SIZE:
                break
            page += 1

        return [self._seance_depuis_activite(a) for a in activites]

    def _get_avec_retry(self, tokens: TokensOAuth, params: dict) -> httpx.Response:
        """Retente automatiquement sur une limite de débit (429) ou une erreur transport
        transitoire (timeout, connexion) plutôt que d'échouer silencieusement/partiellement
        (FR-003) ; dégrade en `PlateformeIndisponibleError` après `RATE_LIMIT_TENTATIVES_MAX`
        tentatives (research.md Decision 3)."""
        for tentative in range(RATE_LIMIT_TENTATIVES_MAX):
            try:
                reponse = httpx.get(
                    ACTIVITES_URL,
                    headers={"Authorization": f"Bearer {tokens.access_token}"},
                    params=params,
                    timeout=REQUEST_TIMEOUT_SECONDES,
                )
            except httpx.TransportError as exc:
                if tentative == RATE_LIMIT_TENTATIVES_MAX - 1:
                    raise PlateformeIndisponibleError("Strava API injoignable") from exc
                time.sleep(RATE_LIMIT_ATTENTE_SECONDES)
                continue

            if reponse.status_code == 429:
                if tentative == RATE_LIMIT_TENTATIVES_MAX - 1:
                    raise PlateformeIndisponibleError("Strava API : limite de débit dépassée")
                time.sleep(RATE_LIMIT_ATTENTE_SECONDES)
                continue

            if reponse.status_code == 401:
                raise TokenInvalideError("Token Strava refusé")
            if reponse.status_code >= 500:
                raise PlateformeIndisponibleError(f"Strava API indisponible ({reponse.status_code})")
            reponse.raise_for_status()
            return reponse

        raise PlateformeIndisponibleError("Strava API : limite de débit dépassée")

    def revoquer(self, tokens: TokensOAuth) -> None:
        httpx.post(DEAUTHORIZE_URL, params={"access_token": tokens.access_token})

    @staticmethod
    def _tokens_depuis_reponse(reponse: httpx.Response) -> TokensOAuth:
        if reponse.status_code == 401:
            raise TokenInvalideError("Token Strava refusé")
        if reponse.status_code >= 500:
            raise PlateformeIndisponibleError(f"Strava API indisponible ({reponse.status_code})")
        reponse.raise_for_status()
        data = reponse.json()
        expire_le = (
            datetime.fromtimestamp(data["expires_at"], tz=UTC)
            if "expires_at" in data
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
            date_debut=datetime.fromisoformat(activite["start_date"].replace("Z", "+00:00")),
            duree_secondes=activite["elapsed_time"],
            distance_metres=activite.get("distance"),
            puissance_moyenne_watts=activite.get("average_watts"),
            frequence_cardiaque_moyenne=(
                round(activite["average_heartrate"]) if activite.get("average_heartrate") else None
            ),
            denivele_metres=activite.get("total_elevation_gain"),
        )
