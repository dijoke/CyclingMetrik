"""Initial schema: athlete, connexion_plateforme, seance, charge_entrainement, recommandation

Revision ID: 0001
Revises:
Create Date: 2026-08-15

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "athlete",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("poids_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("taille_cm", sa.Integer, nullable=True),
        sa.Column("objectifs", sa.String, nullable=True),
        sa.Column("contraintes_alimentaires", postgresql.ARRAY(sa.String), nullable=False),
        sa.Column("date_creation", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_derniere_maj_profil", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("poids_kg IS NULL OR poids_kg > 0", name="ck_athlete_poids_positif"),
        sa.CheckConstraint("taille_cm IS NULL OR taille_cm > 0", name="ck_athlete_taille_positive"),
    )

    # create_type=False : le type est créé explicitement ci-dessous ; sans ce flag,
    # op.create_table() tente de le recréer automatiquement (DuplicateObject).
    plateforme_enum = postgresql.ENUM(
        "garmin_connect", "strava", "nolio", name="plateforme_enum", create_type=False
    )
    statut_connexion_enum = postgresql.ENUM(
        "actif", "expire", "revoque", name="statut_connexion_enum", create_type=False
    )
    plateforme_enum.create(op.get_bind())
    statut_connexion_enum.create(op.get_bind())

    op.create_table(
        "connexion_plateforme",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "athlete_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("athlete.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("plateforme", plateforme_enum, nullable=False),
        sa.Column("statut", statut_connexion_enum, nullable=False, server_default="actif"),
        sa.Column("access_token_chiffre", sa.LargeBinary, nullable=False),
        sa.Column("refresh_token_chiffre", sa.LargeBinary, nullable=True),
        sa.Column("date_expiration_token", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_derniere_synchronisation", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_connexion", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("athlete_id", "plateforme", name="uq_connexion_athlete_plateforme"),
    )

    statut_donnees_seance_enum = postgresql.ENUM(
        "valide",
        "aberrant",
        "doublon_probable",
        name="statut_donnees_seance_enum",
        create_type=False,
    )
    statut_donnees_seance_enum.create(op.get_bind())

    op.create_table(
        "seance",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "athlete_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("athlete.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "connexion_plateforme_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("connexion_plateforme.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("id_externe", sa.String(255), nullable=False),
        sa.Column("date_debut", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duree_secondes", sa.Integer, nullable=False),
        sa.Column("distance_metres", sa.Numeric(10, 2), nullable=True),
        sa.Column("puissance_moyenne_watts", sa.Numeric(6, 2), nullable=True),
        sa.Column("frequence_cardiaque_moyenne", sa.Integer, nullable=True),
        sa.Column("denivele_metres", sa.Numeric(8, 2), nullable=True),
        sa.Column(
            "statut_donnees",
            statut_donnees_seance_enum,
            nullable=False,
            server_default="valide",
        ),
        sa.Column(
            "seance_doublon_de_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("seance.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("date_import", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("connexion_plateforme_id", "id_externe", name="uq_seance_source"),
        sa.CheckConstraint("duree_secondes > 0", name="ck_seance_duree_positive"),
    )

    tendance_charge_enum = postgresql.ENUM(
        "progression",
        "surcharge",
        "recuperation",
        "stable",
        name="tendance_charge_enum",
        create_type=False,
    )
    tendance_charge_enum.create(op.get_bind())

    op.create_table(
        "charge_entrainement",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "athlete_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("athlete.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date_calcul", sa.DateTime(timezone=True), nullable=False),
        sa.Column("charge_aigue_7j", sa.Numeric(8, 2), nullable=True),
        sa.Column("charge_chronique_28j", sa.Numeric(8, 2), nullable=True),
        sa.Column("ratio_acwr", sa.Numeric(5, 2), nullable=True),
        sa.Column("tendance", tendance_charge_enum, nullable=True),
        sa.Column("donnees_suffisantes", sa.Boolean, nullable=False),
    )

    type_recommandation_enum = postgresql.ENUM(
        "recuperation", "nutrition", name="type_recommandation_enum", create_type=False
    )
    statut_recommandation_enum = postgresql.ENUM(
        "disponible",
        "donnees_insuffisantes",
        name="statut_recommandation_enum",
        create_type=False,
    )
    type_recommandation_enum.create(op.get_bind())
    statut_recommandation_enum.create(op.get_bind())

    op.create_table(
        "recommandation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "athlete_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("athlete.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", type_recommandation_enum, nullable=False),
        sa.Column("date_generation", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "seance_declenchante_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("seance.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("statut", statut_recommandation_enum, nullable=False),
        sa.Column("contenu", postgresql.JSONB, nullable=True),
        sa.Column("motif_donnees_insuffisantes", sa.String, nullable=True),
        sa.Column("justification", postgresql.JSONB, nullable=True),
        sa.CheckConstraint(
            "(statut = 'disponible' AND contenu IS NOT NULL AND justification IS NOT NULL) OR "
            "(statut = 'donnees_insuffisantes' AND contenu IS NULL AND motif_donnees_insuffisantes IS NOT NULL)",
            name="ck_recommandation_invariant_principe_1",
        ),
    )


def downgrade() -> None:
    op.drop_table("recommandation")
    op.drop_table("charge_entrainement")
    op.drop_table("seance")
    op.drop_table("connexion_plateforme")
    op.drop_table("athlete")

    for enum_name in (
        "statut_recommandation_enum",
        "type_recommandation_enum",
        "tendance_charge_enum",
        "statut_donnees_seance_enum",
        "statut_connexion_enum",
        "plateforme_enum",
    ):
        postgresql.ENUM(name=enum_name).drop(op.get_bind())
