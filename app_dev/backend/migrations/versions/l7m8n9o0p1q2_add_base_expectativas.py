"""add base_expectativas - Camada de projeção (sazonais, parcelas futuras)

Revision ID: l7m8n9o0p1q2
Revises: k6l7m8n9o0p1
Create Date: 2026-02-28

Fase 4: base_expectativas conforme TECH_SPEC legado
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "l7m8n9o0p1q2"
down_revision: Union[str, Sequence[str], None] = "k6l7m8n9o0p1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "base_expectativas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.String(200), nullable=True),
        sa.Column("valor", sa.Float(), nullable=False),
        sa.Column("grupo", sa.String(100), nullable=True),
        sa.Column("tipo_lancamento", sa.String(10), nullable=True, server_default="debito"),
        sa.Column("mes_referencia", sa.String(7), nullable=False),
        sa.Column("tipo_expectativa", sa.String(30), nullable=False),
        sa.Column("origem", sa.String(20), nullable=False),
        sa.Column("id_parcela", sa.String(64), nullable=True),
        sa.Column("parcela_seq", sa.Integer(), nullable=True),
        sa.Column("parcela_total", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=True, server_default="pendente"),
        sa.Column("journal_entry_id", sa.Integer(), nullable=True),
        sa.Column("valor_realizado", sa.Float(), nullable=True),
        sa.Column("realizado_em", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_base_expectativas_user_id", "base_expectativas", ["user_id"], unique=False)
    op.create_index("ix_base_expectativas_mes_referencia", "base_expectativas", ["mes_referencia"], unique=False)
    op.create_index("idx_expectativas_user_mes", "base_expectativas", ["user_id", "mes_referencia"], unique=False)
    op.create_index("idx_expectativas_status", "base_expectativas", ["status"], unique=False)
    op.create_unique_constraint(
        "uq_expectativa_parcela",
        "base_expectativas",
        ["user_id", "id_parcela", "parcela_seq"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_expectativa_parcela", "base_expectativas", type_="unique")
    op.drop_index("idx_expectativas_status", table_name="base_expectativas")
    op.drop_index("idx_expectativas_user_mes", table_name="base_expectativas")
    op.drop_index("ix_base_expectativas_mes_referencia", table_name="base_expectativas")
    op.drop_index("ix_base_expectativas_user_id", table_name="base_expectativas")
    op.drop_table("base_expectativas")
