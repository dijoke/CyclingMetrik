# Phase 1 Data Model: Coaching vélo connecté

**Feature**: `001-coaching-velo-garmin-strava` | **Date**: 2026-08-15

Dérivé des Key Entities du spec (§ Key Entities) et des décisions de research.md.

## Athlete

Profil de l'utilisateur, un seul athlète par compte (v1).

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| email | string | unique, requis (identifiant de compte) |
| poids_kg | decimal | nullable — tant que non renseigné, les recommandations nutritionnelles restent en statut "insuffisant" (FR-011) |
| taille_cm | integer | nullable |
| objectifs | text | nullable, libre (ex: "préparation cyclosportive juillet") |
| contraintes_alimentaires | text[] | nullable (ex: végétarien, sans gluten) |
| date_creation | timestamp | requis |
| date_derniere_maj_profil | timestamp | requis, mis à jour à chaque modification de profil |

**Validation**: `poids_kg` et `taille_cm`, si renseignés, doivent être strictement positifs.

**Relations**: 1—N vers `ConnexionPlateforme`, 1—N vers `Seance` (via connexions), 1—N vers `Recommandation`.

## ConnexionPlateforme

Association entre l'athlète et un compte externe (FR-001, FR-009).

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| athlete_id | UUID | FK → Athlete, requis |
| plateforme | enum | `garmin_connect` \| `strava` \| `nolio`, requis |
| statut | enum | `actif` \| `expire` \| `revoque`, requis, défaut `actif` |
| access_token_chiffre | bytes | requis, chiffré at-rest (Principe II) — jamais exposé en clair via l'API |
| refresh_token_chiffre | bytes | nullable (certaines plateformes), chiffré at-rest |
| date_expiration_token | timestamp | nullable |
| date_derniere_synchronisation | timestamp | nullable (jamais synchronisé si null) |
| date_connexion | timestamp | requis |

**Contraintes**: unique (`athlete_id`, `plateforme`) — une seule connexion active par plateforme et par athlète.

**Transitions d'état**: `actif → expire` (token refusé au refresh) ; `actif → revoque` (athlète déconnecte, ou plateforme signale une révocation) ; toute tentative de sync sur `expire`/`revoque` déclenche la notification FR-009, pas de nouvel essai automatique tant que l'athlète n'a pas reconnecté.

## Seance

Un entraînement ou une course importé(e) (FR-002, FR-003).

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| athlete_id | UUID | FK → Athlete, requis |
| connexion_plateforme_id | UUID | FK → ConnexionPlateforme, requis (source d'origine) |
| id_externe | string | requis, identifiant de la séance sur la plateforme source |
| date_debut | timestamp | requis |
| duree_secondes | integer | requis, > 0 |
| distance_metres | decimal | nullable |
| puissance_moyenne_watts | decimal | nullable — dépend du capteur (cf. Assumptions du spec) |
| frequence_cardiaque_moyenne | integer | nullable |
| denivele_metres | decimal | nullable |
| statut_donnees | enum | `valide` \| `aberrant` \| `doublon_probable`, requis, défaut `valide` |
| seance_doublon_de_id | UUID | nullable, FK → Seance (auto-référence, renseigné si `statut_donnees = doublon_probable`, cf. research.md §7) |
| date_import | timestamp | requis |

**Contraintes**: unique (`connexion_plateforme_id`, `id_externe`) — pas de double-import de la même séance source.

**Validation "données aberrantes" (edge case du spec)**: une séance est marquée `aberrant` si `frequence_cardiaque_moyenne` sort d'une plage physiologique plausible (ex. < 30 ou > 240 bpm) ou si `duree_secondes` est incohérente avec `distance_metres` (vitesse moyenne implausible). Une séance `aberrant` est exclue du calcul de charge (US2) et ne peut pas fonder une recommandation (US3, FR-011).

**Relations**: N—1 vers `Athlete`, N—1 vers `ConnexionPlateforme`, 1—N vers `Recommandation` (une séance significative peut motiver une recommandation).

## ChargeEntrainement

Indicateur agrégé calculé sur une période, pas stocké séance par séance mais en instantané périodique pour l'historique de tendance (US2).

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| athlete_id | UUID | FK → Athlete, requis |
| date_calcul | timestamp | requis |
| charge_aigue_7j | decimal | requis, calculé à partir des `Seance` valides des 7 derniers jours |
| charge_chronique_28j | decimal | requis, calculé à partir des `Seance` valides des 28 derniers jours |
| ratio_acwr | decimal | requis, `charge_aigue_7j / charge_chronique_28j` (research.md §5) |
| tendance | enum | `progression` \| `surcharge` \| `recuperation` \| `stable`, requis |
| donnees_suffisantes | boolean | requis — `false` si historique < 2 semaines (FR spec US2, Acceptance Scenario 3) |

**Règle de dérivation de `tendance`** (seuils ACWR usuels en science du sport, à valider en implémentation) : `ratio_acwr > 1.5` → `surcharge` ; `ratio_acwr < 0.8` → `recuperation` ; sinon `stable` ou `progression` selon la pente de `charge_chronique_28j` sur les 4 dernières semaines (FR-004, Acceptance Scenario 1).

**Relations**: N—1 vers `Athlete`.

## Recommandation

Conseil généré (récupération ou nutrition), avec sa justification (FR-006, FR-007, FR-011, Principe I).

| Champ | Type | Contraintes |
|---|---|---|
| id | UUID | PK |
| athlete_id | UUID | FK → Athlete, requis |
| type | enum | `recuperation` \| `nutrition`, requis |
| date_generation | timestamp | requis |
| seance_declenchante_id | UUID | nullable, FK → Seance (recommandation liée à une séance précise) |
| statut | enum | `disponible` \| `donnees_insuffisantes`, requis |
| contenu | jsonb | nullable — structure dépend du type (ex: `{repos_recommande, intensite_lendemain}` pour récupération ; `{calories_kcal, glucides_g, proteines_g, lipides_g}` pour nutrition). `null` si `statut = donnees_insuffisantes` |
| motif_donnees_insuffisantes | text | nullable, requis si `statut = donnees_insuffisantes` (ex: "profil athlète incomplet : poids manquant") |
| justification | jsonb | requis si `statut = disponible` — références aux données sources (ids de séances, valeurs de charge utilisées) pour rester explicable (Principe I) |

**Invariant (NON-NEGOTIABLE, Principe I)**: `statut = disponible` ⟺ `contenu` non nul ET `justification` non nulle. `statut = donnees_insuffisantes` ⟺ `contenu` nul ET `motif_donnees_insuffisantes` renseigné. Cet invariant doit être couvert par un test unitaire avant toute implémentation du moteur de recommandations (Principe IV).

**Relations**: N—1 vers `Athlete`, N—1 vers `Seance` (optionnel).

## Diagramme relationnel (résumé)

```text
Athlete 1───N ConnexionPlateforme 1───N Seance
   │                                      │
   │                                      │ (déclenche, optionnel)
   1───N ChargeEntrainement                │
   │                                      │
   1───N Recommandation ────────────────N─┘ (seance_declenchante_id, optionnel)
```
