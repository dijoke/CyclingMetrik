from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, LargeBinary, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Plateforme(str, enum.Enum):
    GARMIN_CONNECT = "garmin_connect"
    STRAVA = "strava"
    NOLIO = "nolio"


class StatutConnexion(str, enum.Enum):
    ACTIF = "actif"
    EXPIRE = "expire"
    REVOQUE = "revoque"


class ConnexionPlateforme(Base):
    __tablename__ = "connexion_plateforme"
    __table_args__ = (
        UniqueConstraint("athlete_id", "plateforme", name="uq_connexion_athlete_plateforme"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("athlete.id", ondelete="CASCADE"), nullable=False
    )
    plateforme: Mapped[Plateforme] = mapped_column(
        Enum(Plateforme, name="plateforme_enum"), nullable=False
    )
    statut: Mapped[StatutConnexion] = mapped_column(
        Enum(StatutConnexion, name="statut_connexion_enum"),
        default=StatutConnexion.ACTIF,
        nullable=False,
    )
    access_token_chiffre: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    refresh_token_chiffre: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    date_expiration_token: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    date_derniere_synchronisation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    date_connexion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    athlete = relationship("Athlete", backref="connexions")
