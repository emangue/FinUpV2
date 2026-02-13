"""consolidate_budget_tables

Revision ID: 635e060a2434
Revises: 9feefd17fcda
Create Date: 2026-02-13 19:11:12.757172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '635e060a2434'
down_revision: Union[str, Sequence[str], None] = '9feefd17fcda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Consolidação de tabelas budget:
    - Migra dados: budget_geral → budget_planning
    - Remove: budget_geral, budget_categoria_config, budget_geral_historico
    """
    
    # 1. Migrar dados de budget_geral para budget_planning
    # Apenas se não existir já (evita duplicatas)
    op.execute("""
        INSERT INTO budget_planning (
            user_id, 
            grupo, 
            mes_referencia, 
            valor_planejado, 
            valor_medio_3_meses,
            ativo, 
            created_at, 
            updated_at
        )
        SELECT 
            bg.user_id,
            bg.categoria_geral as grupo,
            bg.mes_referencia,
            bg.valor_planejado,
            0.0 as valor_medio_3_meses,
            1 as ativo,
            COALESCE(bg.created_at, CURRENT_TIMESTAMP),
            COALESCE(bg.updated_at, CURRENT_TIMESTAMP)
        FROM budget_geral bg
        WHERE NOT EXISTS (
            SELECT 1 FROM budget_planning bp
            WHERE bp.user_id = bg.user_id
              AND bp.grupo = bg.categoria_geral
              AND bp.mes_referencia = bg.mes_referencia
        )
    """)
    
    # 2. Log de registros migrados (para auditoria)
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT 
            (SELECT COUNT(*) FROM budget_geral) as geral_count,
            (SELECT COUNT(*) FROM budget_planning) as planning_count
    """))
    row = result.fetchone()
    print(f"""
    ═══════════════════════════════════════════════
    📊 MIGRAÇÃO DE BUDGET CONCLUÍDA
    ═══════════════════════════════════════════════
    Registros em budget_geral: {row[0]}
    Registros em budget_planning: {row[1]}
    ═══════════════════════════════════════════════
    """)
    
    # 3. Drop tabelas antigas (ordem importa por FKs)
    op.drop_table('budget_geral_historico')
    op.drop_table('budget_categoria_config')
    op.drop_table('budget_geral')
    
    print("✅ Tabelas removidas: budget_geral, budget_categoria_config, budget_geral_historico")


def downgrade() -> None:
    """
    Downgrade: Recria tabelas vazias (dados não são restaurados)
    ⚠️ ATENÇÃO: Downgrade cria estrutura vazia - dados são perdidos!
    """
    
    # Recriar budget_geral
    op.create_table(
        'budget_geral',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('categoria_geral', sa.String(length=50), nullable=False),
        sa.Column('mes_referencia', sa.String(length=7), nullable=False),
        sa.Column('valor_planejado', sa.Float(), nullable=False),
        sa.Column('total_mensal', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_budget_geral_user_id', 'budget_geral', ['user_id'])
    op.create_index('ix_budget_geral_mes_referencia', 'budget_geral', ['mes_referencia'])
    
    # Recriar budget_categoria_config
    op.create_table(
        'budget_categoria_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('nome_categoria', sa.String(length=100), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=False),
        sa.Column('fonte_dados', sa.String(length=20), nullable=False),
        sa.Column('filtro_valor', sa.String(length=100), nullable=False),
        sa.Column('tipos_gasto_incluidos', sa.String(length=1000), nullable=True),
        sa.Column('cor_visualizacao', sa.String(length=7), nullable=False),
        sa.Column('ativo', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_budget_categoria_config_user_id', 'budget_categoria_config', ['user_id'])
    
    # Recriar budget_geral_historico
    op.create_table(
        'budget_geral_historico',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mes_referencia', sa.String(length=7), nullable=False),
        sa.Column('valor_anterior', sa.Float(), nullable=False),
        sa.Column('valor_novo', sa.Float(), nullable=False),
        sa.Column('motivo', sa.String(length=500), nullable=False),
        sa.Column('soma_categorias', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_budget_geral_historico_user_id', 'budget_geral_historico', ['user_id'])
    op.create_index('ix_budget_geral_historico_mes_referencia', 'budget_geral_historico', ['mes_referencia'])
    
    print("""
    ⚠️  DOWNGRADE EXECUTADO
    ═══════════════════════════════════════════════
    Tabelas recriadas vazias:
    - budget_geral
    - budget_categoria_config
    - budget_geral_historico
    
    ⚠️  ATENÇÃO: Dados não foram restaurados!
    Para restaurar, use backup do banco.
    ═══════════════════════════════════════════════
    """)
