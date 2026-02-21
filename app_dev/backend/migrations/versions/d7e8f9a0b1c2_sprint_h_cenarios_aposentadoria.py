"""Sprint H: Cenários aposentadoria - novos campos + projeção mês a mês

Revision ID: d7e8f9a0b1c2
Revises: c3d4e5f6a7b8
Create Date: 2026-02-21

- investimentos_cenarios: idade_atual, idade_aposentadoria, renda_mensal_alvo,
  inflacao_aa, retorno_aa, extras_json, anomes_inicio, principal
- Nova tabela investimentos_cenario_projecao (mes_num, anomes, patrimonio)

Nota: Se colunas/tabela já existirem (ex: aplicado manualmente), upgrade é no-op.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'd7e8f9a0b1c2'
down_revision = 'c3d4e5f6a7b8'  # remove_investimentos_from_budget_planning
branch_labels = None
depends_on = None


def _column_exists(conn, table: str, column: str) -> bool:
    insp = inspect(conn)
    cols = [c['name'] for c in insp.get_columns(table)]
    return column in cols


def _table_exists(conn, table: str) -> bool:
    insp = inspect(conn)
    return table in insp.get_table_names()


def upgrade() -> None:
    conn = op.get_bind()
    # Novos campos em investimentos_cenarios (só adiciona se não existir)
    if not _column_exists(conn, 'investimentos_cenarios', 'idade_atual'):
        op.add_column('investimentos_cenarios', sa.Column('idade_atual', sa.Integer(), nullable=True))
    if not _column_exists(conn, 'investimentos_cenarios', 'idade_aposentadoria'):
        op.add_column('investimentos_cenarios', sa.Column('idade_aposentadoria', sa.Integer(), nullable=True))
    if not _column_exists(conn, 'investimentos_cenarios', 'renda_mensal_alvo'):
        op.add_column('investimentos_cenarios', sa.Column('renda_mensal_alvo', sa.Numeric(15, 2), nullable=True))
    if not _column_exists(conn, 'investimentos_cenarios', 'inflacao_aa'):
        op.add_column('investimentos_cenarios', sa.Column('inflacao_aa', sa.Numeric(6, 2), nullable=True))
    if not _column_exists(conn, 'investimentos_cenarios', 'retorno_aa'):
        op.add_column('investimentos_cenarios', sa.Column('retorno_aa', sa.Numeric(6, 2), nullable=True))
    if not _column_exists(conn, 'investimentos_cenarios', 'anomes_inicio'):
        op.add_column('investimentos_cenarios', sa.Column('anomes_inicio', sa.Integer(), nullable=True))
    if not _column_exists(conn, 'investimentos_cenarios', 'principal'):
        op.add_column('investimentos_cenarios', sa.Column('principal', sa.Boolean(), nullable=True))
    if not _column_exists(conn, 'investimentos_cenarios', 'extras_json'):
        op.add_column('investimentos_cenarios', sa.Column('extras_json', sa.Text(), nullable=True))

    # Tabela investimentos_cenario_projecao (só cria se não existir)
    if not _table_exists(conn, 'investimentos_cenario_projecao'):
        op.create_table(
            'investimentos_cenario_projecao',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('cenario_id', sa.Integer(), nullable=False),
            sa.Column('mes_num', sa.Integer(), nullable=False),
            sa.Column('anomes', sa.Integer(), nullable=False),
            sa.Column('patrimonio', sa.Numeric(15, 2), nullable=False),
            sa.ForeignKeyConstraint(['cenario_id'], ['investimentos_cenarios.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_cenario_projecao_cenario', 'investimentos_cenario_projecao', ['cenario_id'])
        op.create_index('idx_cenario_projecao_anomes', 'investimentos_cenario_projecao', ['cenario_id', 'anomes'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_cenario_projecao_anomes', table_name='investimentos_cenario_projecao')
    op.drop_index('idx_cenario_projecao_cenario', table_name='investimentos_cenario_projecao')
    op.drop_table('investimentos_cenario_projecao')

    op.drop_column('investimentos_cenarios', 'extras_json')
    op.drop_column('investimentos_cenarios', 'principal')
    op.drop_column('investimentos_cenarios', 'anomes_inicio')
    op.drop_column('investimentos_cenarios', 'retorno_aa')
    op.drop_column('investimentos_cenarios', 'inflacao_aa')
    op.drop_column('investimentos_cenarios', 'renda_mensal_alvo')
    op.drop_column('investimentos_cenarios', 'idade_aposentadoria')
    op.drop_column('investimentos_cenarios', 'idade_atual')
