"""remove_investimentos_from_budget_planning - Sprint E

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-21

Sprint E: Remover metas de Investimentos do budget_planning.
Fonte de aporte planejado passa a ser exclusivamente o cenário de aposentadoria.
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove registros de budget_planning cujo grupo tem categoria_geral='Investimentos'.
    A categoria vem de base_grupos_config (grupo = nome_grupo).
    """
    op.execute("""
        DELETE FROM budget_planning
        WHERE grupo IN (
            SELECT nome_grupo FROM base_grupos_config
            WHERE categoria_geral = 'Investimentos'
        )
    """)


def downgrade() -> None:
    """
    Não é possível restaurar os dados deletados.
    Downgrade é no-op (dados já foram removidos).
    """
    pass
