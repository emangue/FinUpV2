"""add_cor_to_base_grupos_config - Sprint C

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-20

Sprint C: Central de Grupos - coluna cor para paleta de 11 grupos
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('base_grupos_config', sa.Column('cor', sa.String(7), nullable=True))


def downgrade() -> None:
    op.drop_column('base_grupos_config', 'cor')
