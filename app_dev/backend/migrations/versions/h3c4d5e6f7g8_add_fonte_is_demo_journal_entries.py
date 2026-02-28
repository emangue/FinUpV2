"""add_fonte_is_demo_journal_entries - Onboarding modo demo

Revision ID: h3c4d5e6f7g8
Revises: g2b3c4d5e6f7
Create Date: 2026-02-28

Adiciona fonte (string) e is_demo (boolean) em journal_entries para suportar modo exploração.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "h3c4d5e6f7g8"
down_revision: Union[str, Sequence[str], None] = "g2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    is_sqlite = "sqlite" in str(conn.engine.url)

    op.add_column("journal_entries", sa.Column("fonte", sa.String(), nullable=True))
    op.add_column(
        "journal_entries",
        sa.Column("is_demo", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.create_index("ix_journal_entries_fonte", "journal_entries", ["fonte"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_journal_entries_fonte", table_name="journal_entries")
    op.drop_column("journal_entries", "is_demo")
    op.drop_column("journal_entries", "fonte")
