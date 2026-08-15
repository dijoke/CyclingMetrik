from __future__ import annotations

from dataclasses import dataclass

FENETRES_SECONDES = {
    "puissance_max_1min": 60,
    "puissance_max_3min": 180,
    "puissance_max_5min": 300,
    "puissance_max_10min": 600,
    "puissance_max_20min": 1200,
}


@dataclass
class RecordsPuissanceSeance:
    puissance_max_1min: float | None
    puissance_max_3min: float | None
    puissance_max_5min: float | None
    puissance_max_10min: float | None
    puissance_max_20min: float | None


def _meilleure_moyenne_glissante(watts: list[int], fenetre: int) -> float | None:
    """Meilleure moyenne sur une fenêtre glissante de `fenetre` secondes, en supposant un flux
    à 1Hz (research.md Decision 3). `None` si le flux est plus court que la fenêtre (FR-006)."""
    if len(watts) < fenetre:
        return None
    somme = sum(watts[:fenetre])
    meilleure = somme
    for i in range(fenetre, len(watts)):
        somme += watts[i] - watts[i - fenetre]
        if somme > meilleure:
            meilleure = somme
    return round(meilleure / fenetre, 1)


def calculer_records_puissance(watts: list[int] | None) -> RecordsPuissanceSeance:
    """Meilleure puissance moyenne glissante sur chaque durée de référence (1/3/5/10/20 min), à
    partir du flux de puissance seconde par seconde d'une séance. `None` par champ si le flux est
    absent/vide, ou si la séance est plus courte que la durée concernée — jamais une valeur par
    défaut trompeuse (FR-006)."""
    if not watts:
        return RecordsPuissanceSeance(None, None, None, None, None)

    valeurs = {champ: _meilleure_moyenne_glissante(watts, fenetre) for champ, fenetre in FENETRES_SECONDES.items()}
    return RecordsPuissanceSeance(**valeurs)
