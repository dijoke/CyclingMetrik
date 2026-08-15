# Contrat interne : connecteur de plateforme source

**Feature**: `001-coaching-velo-garmin-strava` | Complète `api.openapi.yaml`

Chaque plateforme source (Garmin Connect, Strava, Nolio) est intégrée via un connecteur qui implémente cette interface commune. Les tests de contrat (`backend/tests/contract/`, Principe IV) valident cette interface avec des fixtures rejouables par plateforme, pour détecter tout changement de format d'API en amont.

## Interface

```python
class PlateformeConnecteur(Protocol):
    def url_autorisation(self, redirect_uri: str, state: str) -> str:
        """Construit l'URL du flux OAuth de la plateforme (FR-001)."""

    def echanger_code(self, code: str, redirect_uri: str) -> TokensOAuth:
        """Échange le code d'autorisation contre access_token/refresh_token."""

    def rafraichir_token(self, refresh_token: str) -> TokensOAuth:
        """Rafraîchit un token expiré. Lève TokenInvalideError si refus (→ FR-009)."""

    def recuperer_seances(self, tokens: TokensOAuth, depuis: datetime) -> list[SeanceBrute]:
        """Récupère les séances depuis une date donnée, non transformées."""

    def revoquer(self, tokens: TokensOAuth) -> None:
        """Révoque l'accès côté plateforme lors d'une déconnexion athlète."""
```

## Contrat de sortie : `SeanceBrute`

Chaque connecteur DOIT normaliser la réponse de sa plateforme vers cette structure commune avant remise au service d'import (qui la transforme ensuite en `Seance`, cf. data-model.md) :

| Champ | Type | Note |
|---|---|---|
| id_externe | string | identifiant unique côté plateforme |
| date_debut | datetime (UTC) | requis |
| duree_secondes | int | requis |
| distance_metres | float \| None | absent si non fourni par la plateforme |
| puissance_moyenne_watts | float \| None | absent si pas de capteur de puissance |
| frequence_cardiaque_moyenne | int \| None | |
| denivele_metres | float \| None | |

## Erreurs attendues (contrat commun aux 3 connecteurs)

- `TokenInvalideError` : token expiré/révoqué côté plateforme → le service d'import DOIT passer `ConnexionPlateforme.statut = expire` et déclencher la notification FR-009, sans lever d'exception non gérée.
- `PlateformeIndisponibleError` : API source temporairement indisponible (edge case du spec) → la synchronisation est reportée au prochain cycle planifié (research.md §3), aucune donnée partielle n'est persistée.

## Fixtures de test de contrat

`backend/tests/contract/fixtures/{garmin,strava,nolio}/` — réponses JSON représentatives capturées par plateforme (succès, token expiré, séance avec puissance, séance sans puissance, page vide). Chaque connecteur doit produire un `SeanceBrute` valide (ou l'erreur attendue) pour chaque fixture. Un changement de format d'API en amont fait échouer ces tests avant tout déploiement.
