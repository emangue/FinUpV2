"""add_investimentos_transacoes
Revision ID: e5dddf310d7b
Revises: c3402eb17497
Cria tabela investimentos_transacoes vazia. Compativel com SQLite e PostgreSQL.
"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision = 'e5dddf310d7b'
down_revision = 'c3402eb17497'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('investimentos_transacoes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('investimento_id', sa.Integer(), sa.ForeignKey('investimentos_portfolio.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tipo', sa.String(30), nullable=False),
        sa.Column('valor', sa.Numeric(15, 2), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('anomes', sa.Integer(), nullable=False),
        sa.Column('descricao', sa.String(500), nullable=True),
        sa.Column('fonte', sa.String(30), nullable=True, server_default='manual'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_transacao_user_anomes', 'investimentos_transacoes', ['user_id', 'anomes'])
    op.create_index('idx_transacao_user_tipo', 'investimentos_transacoes', ['user_id', 'tipo'])
    op.create_index('idx_transacao_investimento', 'investimentos_transacoes', ['investimento_id'])

def downgrade():
    op.drop_index('idx_transacao_investimento', table_name='investimentos_transacoes')
    op.drop_index('idx_transacao_user_tipo', table_name='investimentos_transacoes')
    op.drop_index('idx_transacao_user_anomes', table_name='investimentos_transacoes')
    op.drop_table('investimentos_transacoes')
