from __future__ import annotations

from src.services.training_load.calcul_charge import ChargeResultat

REPOS_COMPLET = "repos_complet"
SEANCE_LEGERE = "seance_legere"
ENTRAINEMENT_NORMAL = "entrainement_normal"


def generer_recommandation_recuperation(charge: ChargeResultat) -> dict | None:
    """Retourne le contenu de la recommandation, ou None si la charge n'est pas exploitable."""
    if not charge.donnees_suffisantes or charge.ratio_acwr is None:
        return None

    if charge.tendance == "surcharge":
        intensite = REPOS_COMPLET
        repos = "Repos complet recommandé, sommeil prioritaire ce soir."
    elif charge.tendance == "recuperation":
        intensite = ENTRAINEMENT_NORMAL
        repos = "Charge basse : tu peux reprendre une intensité normale."
    else:
        intensite = SEANCE_LEGERE
        repos = "Séance légère recommandée demain pour bien absorber la charge récente."

    return {"intensite_lendemain": intensite, "repos_recommande": repos}
