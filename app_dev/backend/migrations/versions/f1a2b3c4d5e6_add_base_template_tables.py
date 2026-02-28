"""add_base_template_tables - Grupos por usuário

Revision ID: f1a2b3c4d5e6
Revises: 833cabc081aa
Create Date: 2026-02-28

Cria base_grupos_template e base_marcacoes_template.
Fonte para copiar ao criar novo usuário. Popula de generic_classification_rules + base_grupos_config.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "833cabc081aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Criar base_grupos_template
    op.create_table(
        "base_grupos_template",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nome_grupo", sa.String(100), nullable=False),
        sa.Column("tipo_gasto_padrao", sa.String(50), nullable=False),
        sa.Column("categoria_geral", sa.String(50), nullable=False),
        sa.Column("cor", sa.String(7), nullable=True),
    )
    op.create_unique_constraint("uq_base_grupos_template_nome", "base_grupos_template", ["nome_grupo"])

    # 2. Criar base_marcacoes_template
    op.create_table(
        "base_marcacoes_template",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("GRUPO", sa.String(100), nullable=False),
        sa.Column("SUBGRUPO", sa.String(100), nullable=False),
    )
    op.create_unique_constraint(
        "uq_base_marcacoes_template_grupo_sub", "base_marcacoes_template", ["GRUPO", "SUBGRUPO"]
    )

    # 3. Popular base_grupos_template de base_grupos_config (conjunto completo atual)
    conn = op.get_bind()
    conn.execute(
        text("""
            INSERT INTO base_grupos_template (nome_grupo, tipo_gasto_padrao, categoria_geral, cor)
            SELECT nome_grupo, tipo_gasto_padrao, categoria_geral, cor FROM base_grupos_config
        """)
    )

    # 4. Popular base_marcacoes_template de base_marcacoes
    conn.execute(
        text("""
            INSERT INTO base_marcacoes_template ("GRUPO", "SUBGRUPO")
            SELECT DISTINCT "GRUPO", "SUBGRUPO" FROM base_marcacoes
        """)
    )


def downgrade() -> None:
    op.drop_table("base_marcacoes_template")
    op.drop_table("base_grupos_template")
