"""Sprint H: Adicionar aporte à projeção mês a mês

Revision ID: e8f9a0b1c2d3
Revises: d7e8f9a0b1c2
Create Date: 2026-02-21

- investimentos_cenario_projecao: coluna aporte (aporte planejado do mês)
  Usado como meta/plano para comparar com realização.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = 'e8f9a0b1c2d3'
down_revision = 'd7e8f9a0b1c2'
branch_labels = None
depends_on = None


def _column_exists(conn, table: str, column: str) -> bool:
    insp = inspect(conn)
    cols = [c['name'] for c in insp.get_columns(table)]
    return column in cols


def upgrade() -> None:
    conn = op.get_bind()
    if not _column_exists(conn, 'investimentos_cenario_projecao', 'aporte'):
        op.add_column(
            'investimentos_cenario_projecao',
            sa.Column('aporte', sa.Numeric(15, 2), nullable=True)
        )


def downgrade() -> None:
    op.drop_column('investimentos_cenario_projecao', 'aporte')
