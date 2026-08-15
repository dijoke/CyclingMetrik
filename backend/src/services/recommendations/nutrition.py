from __future__ import annotations

from src.models.athlete import Athlete
from src.services.training_load.calcul_charge import ChargeResultat

KCAL_PAR_KG_BASE = 30  # besoin de base approximatif (repos) par kg
KCAL_PAR_UNITE_CHARGE = 0.05  # surcoût calorique par point de charge aiguë
RATIO_GLUCIDES_CALORIES = 0.55
GRAMMES_PROTEINES_PAR_KG = 1.6


def generer_estimation_nutrition(
    athlete: Athlete, charge: ChargeResultat
) -> tuple[dict | None, str | None]:
    """Retourne (contenu, motif_insuffisance) — exactement un des deux est non nul."""
    if athlete.poids_kg is None:
        return None, "profil athlète incomplet : poids manquant"
    if not charge.donnees_suffisantes or charge.charge_aigue_7j is None:
        return None, "historique de séances insuffisant pour estimer les besoins nutritionnels"

    poids = float(athlete.poids_kg)
    besoin_base = poids * KCAL_PAR_KG_BASE
    surcout_activite = charge.charge_aigue_7j * KCAL_PAR_UNITE_CHARGE
    calories = round(besoin_base + surcout_activite)

    glucides_g = round((calories * RATIO_GLUCIDES_CALORIES) / 4)
    proteines_g = round(poids * GRAMMES_PROTEINES_PAR_KG)
    lipides_g = max(round((calories - (glucides_g * 4) - (proteines_g * 4)) / 9), 0)

    return (
        {
            "calories_kcal": calories,
            "glucides_g": glucides_g,
            "proteines_g": proteines_g,
            "lipides_g": lipides_g,
        },
        None,
    )
