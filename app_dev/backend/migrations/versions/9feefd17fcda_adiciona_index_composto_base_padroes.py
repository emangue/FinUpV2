"""adiciona_index_composto_base_padroes

Revision ID: 9feefd17fcda
Revises: 6977f246014c
Create Date: 2026-02-09 18:58:06.183050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9feefd17fcda'
down_revision: Union[str, Sequence[str], None] = '6977f246014c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona índice composto em base_padroes para otimizar queries
    
    Índice: (padrao_estabelecimento, user_id)
    Benefícios:
    - Acelera buscas por padrão específico de um usuário
    - Previne duplicatas silenciosas
    - Melhora performance de updates
    """
    # Criar índice composto (se não existir)
    op.create_index(
        'ix_base_padroes_estabelecimento_user',
        'base_padroes',
        ['padrao_estabelecimento', 'user_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove índice composto."""
    op.drop_index('ix_base_padroes_estabelecimento_user', table_name='base_padroes')
