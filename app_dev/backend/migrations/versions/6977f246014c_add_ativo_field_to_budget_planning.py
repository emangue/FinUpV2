"""add_ativo_field_to_budget_planning

Revision ID: 6977f246014c
Revises: f6f307855c81
Create Date: 2026-02-08 13:12:04.193510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6977f246014c'
down_revision: Union[str, Sequence[str], None] = 'f6f307855c81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona campo 'ativo' à tabela budget_planning."""
    # Adicionar coluna ativo (boolean) com default TRUE
    op.add_column('budget_planning', sa.Column('ativo', sa.Boolean(), nullable=False, server_default='1'))
    
    # Criar índice para melhorar performance de queries com filtro ativo
    op.create_index('ix_budget_planning_ativo', 'budget_planning', ['ativo'])


def downgrade() -> None:
    """Remove campo 'ativo' da tabela budget_planning."""
    # Remover índice
    op.drop_index('ix_budget_planning_ativo', table_name='budget_planning')
    
    # Remover coluna
    op.drop_column('budget_planning', 'ativo')
