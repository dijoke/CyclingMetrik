from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class StatutDonneesSeance(str, enum.Enum):
    VALIDE = "valide"
    ABERRANT = "aberrant"
    DOUBLON_PROBABLE = "doublon_probable"


class Seance(Base):
    __tablename__ = "seance"
    __table_args__ = (
        UniqueConstraint("connexion_plateforme_id", "id_externe", name="uq_seance_source"),
        CheckConstraint("duree_secondes > 0", name="ck_seance_duree_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("athlete.id", ondelete="CASCADE"), nullable=False
    )
    connexion_plateforme_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("connexion_plateforme.id", ondelete="CASCADE"), nullable=False
    )
    id_externe: Mapped[str] = mapped_column(String(255), nullable=False)
    date_debut: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duree_secondes: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_metres: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    puissance_moyenne_watts: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    frequence_cardiaque_moyenne: Mapped[int | None] = mapped_column(Integer, nullable=True)
    denivele_metres: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    statut_donnees: Mapped[StatutDonneesSeance] = mapped_column(
        Enum(StatutDonneesSeance, name="statut_donnees_seance_enum"),
        default=StatutDonneesSeance.VALIDE,
        nullable=False,
    )
    seance_doublon_de_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("seance.id", ondelete="SET NULL"), nullable=True
    )
    date_import: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
