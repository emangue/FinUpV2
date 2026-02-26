"""fix_base_padroes_unique_constraint_per_user

Revision ID: 833cabc081aa
Revises: e5dddf310d7b
Create Date: 2026-02-26 00:01:25.420190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '833cabc081aa'
down_revision: Union[str, Sequence[str], None] = 'e5dddf310d7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Corrige a unique constraint de base_padroes.
    Antes: UNIQUE(padrao_num)            → bloqueava mesmo padrão para users diferentes
    Depois: UNIQUE(user_id, padrao_num)  → correto — cada usuário tem seu próprio espaço
    """
    # 1. Remove a constraint antiga (apenas padrao_num)
    op.drop_constraint('base_padroes_padrao_num_key', 'base_padroes', type_='unique')

    # 2. Cria nova constraint composta (user_id, padrao_num)
    op.create_unique_constraint(
        'base_padroes_user_id_padrao_num_key',
        'base_padroes',
        ['user_id', 'padrao_num']
    )


def downgrade() -> None:
    """Reverte para constraint de coluna única (atenção: pode falhar se já houver duplicatas)."""
    op.drop_constraint('base_padroes_user_id_padrao_num_key', 'base_padroes', type_='unique')
    op.create_unique_constraint('base_padroes_padrao_num_key', 'base_padroes', ['padrao_num'])
