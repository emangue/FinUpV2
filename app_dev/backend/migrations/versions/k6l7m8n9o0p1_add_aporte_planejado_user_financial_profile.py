"""add aporte_planejado to user_financial_profile

Revision ID: k6l7m8n9o0p1
Revises: j5k6l7m8n9o0
Create Date: 2026-02-28

Fase 3: Aporte planejado do plano financeiro (usado no cashflow e projeção)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "k6l7m8n9o0p1"
down_revision: Union[str, Sequence[str], None] = "j5k6l7m8n9o0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_financial_profile",
        sa.Column("aporte_planejado", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_financial_profile", "aporte_planejado")
