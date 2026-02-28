"""add_plano_tables - Plano Financeiro Sprint 6

Revision ID: i4j5k6l7m8n9
Revises: h3c4d5e6f7g8
Create Date: 2026-02-28

user_financial_profile, plano_metas_categoria, plano_compromissos
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "i4j5k6l7m8n9"
down_revision: Union[str, Sequence[str], None] = "h3c4d5e6f7g8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_financial_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("renda_mensal_liquida", sa.Float(), nullable=True),
        sa.Column("idade_atual", sa.Integer(), nullable=True),
        sa.Column("idade_aposentadoria", sa.Integer(), nullable=True),
        sa.Column("patrimonio_atual", sa.Float(), nullable=True),
        sa.Column("taxa_retorno_anual", sa.Float(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_financial_profile_user_id", "user_financial_profile", ["user_id"], unique=True)

    op.create_table(
        "plano_metas_categoria",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("grupo", sa.String(100), nullable=False),
        sa.Column("valor_meta", sa.Float(), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plano_metas_categoria_user_id", "plano_metas_categoria", ["user_id"], unique=False)
    op.create_unique_constraint(
        "uq_plano_metas_user_grupo_ano_mes",
        "plano_metas_categoria",
        ["user_id", "grupo", "ano", "mes"],
    )

    op.create_table(
        "plano_compromissos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("valor_mensal", sa.Float(), nullable=False),
        sa.Column("meses_restantes", sa.Integer(), nullable=True),
        sa.Column("grupo", sa.String(100), nullable=True),
        sa.Column("data_inicio", sa.Date(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plano_compromissos_user_id", "plano_compromissos", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("plano_compromissos")
    op.drop_table("plano_metas_categoria")
    op.drop_table("user_financial_profile")
