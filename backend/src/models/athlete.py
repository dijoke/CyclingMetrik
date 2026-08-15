from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import ARRAY, CheckConstraint, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


def _maintenant() -> datetime:
    return datetime.now(UTC)


class Athlete(Base):
    __tablename__ = "athlete"
    __table_args__ = (
        CheckConstraint("poids_kg IS NULL OR poids_kg > 0", name="ck_athlete_poids_positif"),
        CheckConstraint("taille_cm IS NULL OR taille_cm > 0", name="ck_athlete_taille_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    poids_kg: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    taille_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    objectifs: Mapped[str | None] = mapped_column(String, nullable=True)
    contraintes_alimentaires: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_maintenant, nullable=False
    )
    date_derniere_maj_profil: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_maintenant, onupdate=_maintenant, nullable=False
    )
