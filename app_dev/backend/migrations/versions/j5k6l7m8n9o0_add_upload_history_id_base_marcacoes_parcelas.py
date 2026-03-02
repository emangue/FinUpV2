"""add upload_history_id to base_marcacoes and base_parcelas

Revision ID: j5k6l7m8n9o0
Revises: i4j5k6l7m8n9
Create Date: 2026-02-28

A.06 - Rastreabilidade: marcar marcos e parcelas com o upload que os criou
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "j5k6l7m8n9o0"
down_revision: Union[str, Sequence[str], None] = "i4j5k6l7m8n9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "base_marcacoes",
        sa.Column("upload_history_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_base_marcacoes_upload_history_id",
        "base_marcacoes",
        "upload_history",
        ["upload_history_id"],
        ["id"],
    )
    op.create_index(
        "ix_base_marcacoes_upload_history_id",
        "base_marcacoes",
        ["upload_history_id"],
        unique=False,
    )

    op.add_column(
        "base_parcelas",
        sa.Column("upload_history_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_base_parcelas_upload_history_id",
        "base_parcelas",
        "upload_history",
        ["upload_history_id"],
        ["id"],
    )
    op.create_index(
        "ix_base_parcelas_upload_history_id",
        "base_parcelas",
        ["upload_history_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_base_parcelas_upload_history_id", table_name="base_parcelas")
    op.drop_constraint("fk_base_parcelas_upload_history_id", "base_parcelas", type_="foreignkey")
    op.drop_column("base_parcelas", "upload_history_id")

    op.drop_index("ix_base_marcacoes_upload_history_id", table_name="base_marcacoes")
    op.drop_constraint("fk_base_marcacoes_upload_history_id", "base_marcacoes", type_="foreignkey")
    op.drop_column("base_marcacoes", "upload_history_id")
