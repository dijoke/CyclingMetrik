from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class TendanceCharge(str, enum.Enum):
    PROGRESSION = "progression"
    SURCHARGE = "surcharge"
    RECUPERATION = "recuperation"
    STABLE = "stable"


class ChargeEntrainement(Base):
    __tablename__ = "charge_entrainement"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("athlete.id", ondelete="CASCADE"), nullable=False
    )
    date_calcul: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    charge_aigue_7j: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    charge_chronique_28j: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    ratio_acwr: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    tendance: Mapped[TendanceCharge | None] = mapped_column(
        Enum(TendanceCharge, name="tendance_charge_enum"), nullable=True
    )
    donnees_suffisantes: Mapped[bool] = mapped_column(Boolean, nullable=False)
