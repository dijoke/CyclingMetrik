# Research: Historique des séances enrichi (filtres, détail, records de puissance)

**Feature**: `007-historique-des-séances` | **Date**: 2026-08-15

## Decision 1 — Tri/filtre : côté client, aucun changement d'API

**Rationale**: `GET /api/seances` renvoie déjà l'intégralité des séances (~800 aujourd'hui, feature 004). Trier/filtrer côté client (état React) évite tout aller-retour réseau et reste immédiat à ce volume — cohérent avec l'approche déjà retenue pour les statistiques (spec 005 Decision 1, qui elle agrège côté SQL car elle traite des sommes, pas un simple tri d'une liste déjà chargée).

**Alternatives considered**: Tri/filtre via paramètres de requête côté API — écarté pour l'instant (Principe V) ; à reconsidérer si le volume de séances dépasse ce qu'un tri client gère confortablement (plusieurs milliers).

## Decision 2 — Page de détail : nouvel endpoint `GET /api/seances/{id}`, réutilise `SeanceOut` déjà étendu

**Rationale**: Symétrique à `GET /api/seances` (spec 001), filtré sur l'athlète authentifié + l'identifiant demandé, 404 si absent ou n'appartenant pas à l'athlète (Acceptance Scenario 3 de US2). Le même schéma `SeanceOut` (étendu par Decision 3) sert la liste et le détail — pas de duplication de schéma.

**Alternatives considered**: Réutiliser uniquement la liste déjà chargée côté frontend (pas de nouvel appel réseau) — écarté : un lien direct vers `/seances/{id}` (partage, rechargement de page) doit fonctionner sans dépendre d'un état déjà chargé ailleurs dans l'application.

## Decision 3 — Records de puissance : flux Strava "streams", calcul en fenêtre glissante, 5 colonnes nullable sur `Seance`

**Rationale**: Strava expose `GET /activities/{id}/streams?keys=time,watts&key_by_type=true` — un flux temps/puissance seconde par seconde, séparé de la liste d'activités déjà utilisée (feature 001/004). Absent du flux si l'activité n'a pas de capteur de puissance (pas une erreur, juste une clé manquante). Le calcul de la meilleure moyenne glissante sur une fenêtre de N secondes est une fonction pure (liste de watts → 5 valeurs optionnelles), testable indépendamment de tout accès réseau/DB — cohérent avec le Principe IV. Les résultats (pas le flux brut) sont stockés dans 5 nouvelles colonnes nullable sur `Seance` (`puissance_max_1min` … `_20min`) : le flux brut seconde par seconde n'a pas besoin d'être conservé une fois les 5 valeurs calculées.

**Alternatives considered**:
- Stocker le flux brut complet (pour recalcul futur ou vraie courbe de puissance multi-durées) — écarté : volume de stockage significatif (des dizaines de milliers de points par séance × ~800 séances) pour un besoin actuel de seulement 5 valeurs dérivées (Principe V) ; réévaluable si une vraie courbe de puissance continue est demandée plus tard.
- Recalcul à la volée à chaque consultation de la page de détail — écarté : impliquerait un appel Strava (et sa limite de débit) à chaque affichage, alors qu'une valeur calculée une fois ne change plus.

## Decision 4 — Traitement de fond (backfill + nouvelles séances) : nouveau job périodique, marqueur `flux_puissance_traite_le` pour éviter les reprises infinies

**Rationale**: FR-007/FR-008 exigent un traitement de fond qui ne bloque rien et ne retente pas indéfiniment. Un nouveau job APScheduler (même patron que `sync_seances`/`generer_recommandations`, feature 001/004) traite un lot borné de séances à chaque cycle : celles où `flux_puissance_traite_le IS NULL`. Deux cas :
- Séance sans `puissance_moyenne_watts` (pas de capteur) → marquée traitée immédiatement, sans appel réseau (aucune chance d'avoir un flux de puissance).
- Séance avec puissance moyenne → appel du flux Strava, calcul, sauvegarde, puis marquage traité — qu'un résultat ait été obtenu ou non (flux indisponible côté Strava = traité sans résultat, FR-008).

Réutilise le retry/backoff déjà en place pour les limites de débit Strava (feature 004, `_get_avec_retry`). Le lot par cycle reste borné (ex. 20 séances/2 min) pour ne jamais entrer en conflit avec le budget de requêtes du job de synchronisation normal (`sync_seances`, toutes les 15 min) — un backfill de 787 séances à ce rythme prend plusieurs heures, accepté explicitement par l'utilisateur (spec.md Assumptions).

**Alternatives considered**:
- Backfill synchrone déclenché manuellement (bouton "lancer le backfill") — écarté : complexité d'UI pour un besoin ponctuel, un job de fond silencieux suffit et respecte FR-007 ("sans action manuelle").
- File de tâches dédiée (Celery/Redis) — écarté (Principe V), même raisonnement que les jobs existants du projet : APScheduler in-process suffit à l'échelle mono-athlète.

## Résumé des NEEDS CLARIFICATION

Aucun — le périmètre du backfill (US3, Acceptance Scenario 4) a été confirmé explicitement par l'utilisateur avant l'écriture de la spec.
