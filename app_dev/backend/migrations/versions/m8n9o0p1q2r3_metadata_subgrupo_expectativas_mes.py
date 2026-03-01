"""metadata_json + subgrupo em base_expectativas; criar expectativas_mes

Revision ID: m8n9o0p1q2r3
Revises: l7m8n9o0p1q2
Create Date: 2026-02-28

Merge Plano + Aposentadoria (AVALIACAO_MERGE_PLANO_APOSENTADORIA.md):
- base_expectativas: metadata_json, subgrupo (nullable)
- expectativas_mes: tabela materializada para extraordinários expandidos
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "m8n9o0p1q2r3"
down_revision: Union[str, Sequence[str], None] = "l7m8n9o0p1q2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. base_expectativas: metadata_json + subgrupo
    op.add_column("base_expectativas", sa.Column("metadata_json", sa.String(2000), nullable=True))
    op.add_column("base_expectativas", sa.Column("subgrupo", sa.String(100), nullable=True))

    # 2. expectativas_mes — materialização dos extraordinários expandidos
    op.create_table(
        "expectativas_mes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("mes_referencia", sa.String(7), nullable=False),
        sa.Column("grupo", sa.String(100), nullable=True),
        sa.Column("subgrupo", sa.String(100), nullable=True),
        sa.Column("tipo", sa.String(10), nullable=False, server_default="debito"),
        sa.Column("valor", sa.Float(), nullable=False),
        sa.Column("origem_expectativa_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["origem_expectativa_id"], ["base_expectativas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_expectativas_mes_user_id", "expectativas_mes", ["user_id"], unique=False)
    op.create_index("ix_expectativas_mes_mes_referencia", "expectativas_mes", ["mes_referencia"], unique=False)
    op.create_index("idx_expectativas_mes_user_mes", "expectativas_mes", ["user_id", "mes_referencia"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_expectativas_mes_user_mes", table_name="expectativas_mes")
    op.drop_index("ix_expectativas_mes_mes_referencia", table_name="expectativas_mes")
    op.drop_index("ix_expectativas_mes_user_id", table_name="expectativas_mes")
    op.drop_table("expectativas_mes")
    op.drop_column("base_expectativas", "subgrupo")
    op.drop_column("base_expectativas", "metadata_json")
