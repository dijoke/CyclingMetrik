from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class TokensOAuth:
    access_token: str
    refresh_token: str | None
    expire_le: datetime | None


@dataclass(frozen=True)
class SeanceBrute:
    """Séance normalisée par un connecteur, avant transformation en modèle `Seance`."""

    id_externe: str
    date_debut: datetime
    duree_secondes: int
    distance_metres: float | None = None
    puissance_moyenne_watts: float | None = None
    frequence_cardiaque_moyenne: int | None = None
    denivele_metres: float | None = None


class TokenInvalideError(Exception):
    """Le token est refusé/expiré/révoqué par la plateforme source (→ FR-009)."""


class PlateformeIndisponibleError(Exception):
    """L'API de la plateforme source est temporairement indisponible."""


class PlateformeConnecteur(Protocol):
    def url_autorisation(self, redirect_uri: str, state: str) -> str: ...

    def echanger_code(self, code: str, redirect_uri: str) -> TokensOAuth: ...

    def rafraichir_token(self, refresh_token: str) -> TokensOAuth: ...

    def recuperer_seances(self, tokens: TokensOAuth, depuis: datetime | None) -> list[SeanceBrute]: ...

    def revoquer(self, tokens: TokensOAuth) -> None: ...
