from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class TypeRecommandation(str, enum.Enum):
    RECUPERATION = "recuperation"
    NUTRITION = "nutrition"


class StatutRecommandation(str, enum.Enum):
    DISPONIBLE = "disponible"
    DONNEES_INSUFFISANTES = "donnees_insuffisantes"


class Recommandation(Base):
    __tablename__ = "recommandation"
    __table_args__ = (
        # Principe I (NON-NEGOTIABLE) : jamais de contenu sans justification, jamais un
        # statut "disponible" sans données pour le fonder — imposé au niveau base aussi.
        CheckConstraint(
            "(statut = 'disponible' AND contenu IS NOT NULL AND justification IS NOT NULL) OR "
            "(statut = 'donnees_insuffisantes' AND contenu IS NULL AND motif_donnees_insuffisantes IS NOT NULL)",
            name="ck_recommandation_invariant_principe_1",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("athlete.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[TypeRecommandation] = mapped_column(
        Enum(
            TypeRecommandation,
            name="type_recommandation_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    date_generation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    seance_declenchante_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("seance.id", ondelete="SET NULL"), nullable=True
    )
    statut: Mapped[StatutRecommandation] = mapped_column(
        Enum(
            StatutRecommandation,
            name="statut_recommandation_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    contenu: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    motif_donnees_insuffisantes: Mapped[str | None] = mapped_column(String, nullable=True)
    justification: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
